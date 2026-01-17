"""Background task scheduling and management."""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Awaitable, Callable, Dict, List, Optional

from ..settings import Config

LOGGER = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Status of a scheduled task."""

    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


@dataclass
class ScheduledTask:
    """A task scheduled for background execution."""

    task_id: str
    name: str
    status: TaskStatus = TaskStatus.PENDING
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    error: Optional[str] = None
    result: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> Optional[float]:
        """Get task duration in seconds."""
        if self.started_at is None:
            return None
        end_time = self.completed_at or time.time()
        return end_time - self.started_at

    def to_dict(self) -> Dict[str, Any]:
        """Serialize task to dictionary."""
        return {
            "task_id": self.task_id,
            "name": self.name,
            "status": self.status.name,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration": self.duration,
            "error": self.error,
            "metadata": self.metadata,
        }


class BackgroundScheduler:
    """Manages background task execution with concurrency control.

    Features:
    - Configurable max concurrent tasks
    - Task queue with priority
    - Progress tracking
    - Graceful shutdown
    """

    def __init__(self, config: Config) -> None:
        self.config = config
        self.settings = config.proactive
        self._max_concurrent = self.settings.max_concurrent_indexing
        self._queue_size = self.settings.index_queue_size

        self._tasks: Dict[str, ScheduledTask] = {}
        self._queue: asyncio.Queue[tuple[int, str, Callable[[], Awaitable[Any]]]] = (
            asyncio.Queue(maxsize=self._queue_size)
        )
        self._running_count = 0
        self._shutdown = False
        self._workers: List[asyncio.Task[None]] = []
        self._lock = asyncio.Lock()

    @property
    def enabled(self) -> bool:
        return self.settings.enabled

    async def start(self) -> None:
        """Start the background scheduler workers."""
        if not self.enabled:
            LOGGER.info("Background scheduler is disabled")
            return

        self._shutdown = False

        for i in range(self._max_concurrent):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self._workers.append(worker)

        LOGGER.info(
            "Started background scheduler with %d workers",
            self._max_concurrent,
        )

    async def stop(self, timeout: float = 30.0) -> None:
        """Stop the scheduler gracefully."""
        self._shutdown = True

        # Wait for running tasks to complete
        start_time = time.time()
        while self._running_count > 0:
            if time.time() - start_time > timeout:
                LOGGER.warning("Timeout waiting for tasks to complete")
                break
            await asyncio.sleep(0.1)

        # Cancel workers
        for worker in self._workers:
            worker.cancel()

        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()

        LOGGER.info("Background scheduler stopped")

    async def schedule(
        self,
        name: str,
        func: Callable[[], Awaitable[Any]],
        priority: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Schedule a task for background execution.

        Args:
            name: Human-readable task name
            func: Async function to execute
            priority: Lower numbers = higher priority (default 0)
            metadata: Optional metadata to attach to task

        Returns:
            Task ID for tracking
        """
        if not self.enabled:
            LOGGER.debug("Scheduler disabled, executing %s synchronously", name)
            try:
                result = await func()
                return f"sync_{name}"
            except Exception as exc:
                LOGGER.error("Sync execution failed: %s", exc)
                raise

        task_id = str(uuid.uuid4())[:8]
        task = ScheduledTask(
            task_id=task_id,
            name=name,
            metadata=metadata or {},
        )

        async with self._lock:
            self._tasks[task_id] = task

        try:
            await self._queue.put((priority, task_id, func))
            LOGGER.debug("Scheduled task %s: %s", task_id, name)
        except asyncio.QueueFull:
            task.status = TaskStatus.FAILED
            task.error = "Queue is full"
            LOGGER.warning("Failed to schedule task %s: queue full", name)

        return task_id

    async def _worker(self, worker_name: str) -> None:
        """Worker coroutine that processes tasks from the queue."""
        LOGGER.debug("Worker %s started", worker_name)

        while not self._shutdown:
            try:
                # Wait for a task with timeout
                try:
                    priority, task_id, func = await asyncio.wait_for(
                        self._queue.get(),
                        timeout=1.0,
                    )
                except asyncio.TimeoutError:
                    continue

                task = self._tasks.get(task_id)
                if not task:
                    continue

                # Execute the task
                async with self._lock:
                    self._running_count += 1

                task.status = TaskStatus.RUNNING
                task.started_at = time.time()

                try:
                    result = await func()
                    task.status = TaskStatus.COMPLETED
                    task.result = result
                    LOGGER.debug(
                        "Task %s completed in %.2fs",
                        task.name,
                        task.duration,
                    )
                except Exception as exc:
                    task.status = TaskStatus.FAILED
                    task.error = str(exc)
                    LOGGER.error("Task %s failed: %s", task.name, exc)
                finally:
                    task.completed_at = time.time()
                    async with self._lock:
                        self._running_count -= 1
                    self._queue.task_done()

            except asyncio.CancelledError:
                break
            except Exception as exc:
                LOGGER.error("Worker %s error: %s", worker_name, exc)

        LOGGER.debug("Worker %s stopped", worker_name)

    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        """Get task by ID."""
        return self._tasks.get(task_id)

    def get_all_tasks(self) -> List[ScheduledTask]:
        """Get all tasks."""
        return list(self._tasks.values())

    def get_pending_tasks(self) -> List[ScheduledTask]:
        """Get all pending tasks."""
        return [t for t in self._tasks.values() if t.status == TaskStatus.PENDING]

    def get_running_tasks(self) -> List[ScheduledTask]:
        """Get all running tasks."""
        return [t for t in self._tasks.values() if t.status == TaskStatus.RUNNING]

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task."""
        task = self._tasks.get(task_id)
        if not task or task.status != TaskStatus.PENDING:
            return False

        task.status = TaskStatus.CANCELLED
        task.completed_at = time.time()
        return True

    def clear_completed(self, max_age: float = 3600.0) -> int:
        """Clear completed tasks older than max_age seconds."""
        now = time.time()
        cleared = 0

        to_remove = [
            task_id
            for task_id, task in self._tasks.items()
            if task.status
            in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED)
            and task.completed_at
            and now - task.completed_at > max_age
        ]

        for task_id in to_remove:
            del self._tasks[task_id]
            cleared += 1

        return cleared

    def get_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics."""
        status_counts: Dict[str, int] = {}
        for task in self._tasks.values():
            status = task.status.name
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "enabled": self.enabled,
            "workers": len(self._workers),
            "queue_size": self._queue.qsize(),
            "max_queue_size": self._queue_size,
            "running_count": self._running_count,
            "total_tasks": len(self._tasks),
            "tasks_by_status": status_counts,
        }
