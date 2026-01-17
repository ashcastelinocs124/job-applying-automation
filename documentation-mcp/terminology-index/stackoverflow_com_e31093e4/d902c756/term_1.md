# MyAppValueError

**Type:** TECHNICAL_TERM  
**Confidence:** 0.90  
**Source:** https://stackoverflow.com/questions/1319615/how-do-i-declare-custom-exceptions-in-modern-python

## Definition
class definition

## Context
lso, you can at least provide a docstring (and not be forced to use the `pass` keyword):

```
class MyAppValueError(ValueError):
    '''Raise when my specific value is wrong'''
```

Set attributes you create yoursel

## Metadata
```json
{
    "term_type": "TECHNICAL_TERM",
    "confidence": 0.9,
    "frequency": 8,
    "source_url": "https://stackoverflow.com/questions/1319615/how-do-i-declare-custom-exceptions-in-modern-python",
    "metadata": {'extraction_method': 'heuristic', 'language': 'javascript', 'entity_type': 'class'}
}
```
