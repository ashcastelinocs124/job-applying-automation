# ValidationError

**Type:** TECHNICAL_TERM  
**Confidence:** 0.90  
**Source:** https://stackoverflow.com/questions/1319615/how-do-i-declare-custom-exceptions-in-modern-python

## Definition
class definition

## Context
message attribute:

> *Edit: to override something (or pass extra args), do this:*
>
> ```
> class ValidationError(Exception):
>     def __init__(self, message, errors):
>
>         # Call the base class constructo

## Metadata
```json
{
    "term_type": "TECHNICAL_TERM",
    "confidence": 0.9,
    "frequency": 7,
    "source_url": "https://stackoverflow.com/questions/1319615/how-do-i-declare-custom-exceptions-in-modern-python",
    "metadata": {'extraction_method': 'heuristic', 'language': 'javascript', 'entity_type': 'class'}
}
```
