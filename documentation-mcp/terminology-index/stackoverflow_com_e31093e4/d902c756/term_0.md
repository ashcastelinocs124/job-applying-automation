# MyException

**Type:** TECHNICAL_TERM  
**Confidence:** 0.90  
**Source:** https://stackoverflow.com/questions/1319615/how-do-i-declare-custom-exceptions-in-modern-python

## Definition
class definition

## Context
thon?

This is fine unless your exception is really a type of a more specific exception:

```
class MyException(Exception):
    pass
```

Or better (maybe perfect), instead of `pass` give a docstring:

```
class

## Metadata
```json
{
    "term_type": "TECHNICAL_TERM",
    "confidence": 0.9,
    "frequency": 9,
    "source_url": "https://stackoverflow.com/questions/1319615/how-do-i-declare-custom-exceptions-in-modern-python",
    "metadata": {'extraction_method': 'heuristic', 'language': 'javascript', 'entity_type': 'class'}
}
```
