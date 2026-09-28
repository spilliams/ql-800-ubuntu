# todo

There's something I want to refactor about inventory.
We want to select between 3 different formats (tiny, small, full) at the command-line.
We also maybe want to customize how many of those get composed into a single line.
And the tape width should be configurable near the top of the stack too.

I think I need to express each format in relationship to its Aztec code. The reason we don't need a `size_px` on `create_tiny_aztec_label` is because that just generates an aztec code without accompanying labels or text. The single image is its output.
