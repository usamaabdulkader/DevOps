from .linter   import lint_dockerfile
from .compose  import validate_compose
from .image    import advise_base_image
from .image_size import analyze_image_size
from .security  import scan_image

# To add a new tool: create tools/newtool.py, import above, add one line here.
REGISTRY: dict = {
    "Dockerfile Linter":   lint_dockerfile,
    "Compose Validator":   validate_compose,
    "Base Image Advisor":  advise_base_image,
    "Image Size Analyser": analyze_image_size,
    "Security Scanner":    scan_image,
}

def run_tool(tool_name: str, payload: str) -> str:
    fn = REGISTRY.get(tool_name)
    if not fn:
        raise ValueError(f"Unknown tool: '{tool_name}'")
    return fn(payload)