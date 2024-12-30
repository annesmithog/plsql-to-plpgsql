from .element import Element

def smooth(element: Element) -> str:
    """平滑にして返します"""
    return ''.join(elm['code'] for elm in element.tokens)
