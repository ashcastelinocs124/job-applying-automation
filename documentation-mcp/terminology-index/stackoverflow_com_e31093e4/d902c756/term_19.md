# specific

**Type:** TECHNICAL_TERM  
**Confidence:** 0.70  
**Source:** https://stackoverflow.com/questions/1319615/how-do-i-declare-custom-exceptions-in-modern-python

## Definition
No definition available

## Context
custom exceptions in modern Python?

This is fine unless your exception is really a type of a more specific exception:

```
class MyException(Exception):
    pass
```

Or better (maybe perfect), instead of `

## Metadata
```json
{
    "term_type": "TECHNICAL_TERM",
    "confidence": 0.7,
    "frequency": 5,
    "source_url": "https://stackoverflow.com/questions/1319615/how-do-i-declare-custom-exceptions-in-modern-python",
    "metadata": {'extraction_method': 'heuristic'}
}
```
