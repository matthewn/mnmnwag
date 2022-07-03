def get_elided_page_range(num_pages, page_range, *, number=1, on_each_side=2, on_ends=3):
    """
    Modified (SMARTER!) version of a method found in Django 3.2's Paginator.
    This version handles out-of-bounds page # requests w/o throwing errors.
    """
    try:
        if isinstance(number, float) and not number.is_integer():
            raise ValueError
        number = int(number)
    except (TypeError, ValueError):
        number = 1
    if number < 1:
        number = 1
    if number > num_pages:
        number = num_pages

    if num_pages <= (on_each_side + on_ends) * 2:
        yield from page_range
        return

    if number > (1 + on_each_side + on_ends) + 1:
        yield from range(1, on_ends + 1)
        yield '...'
        yield from range(number - on_each_side, number + 1)
    else:
        yield from range(1, number + 1)

    if number < (num_pages - on_each_side - on_ends) - 1:
        yield from range(number + 1, number + on_each_side + 1)
        yield '...'
        yield from range(num_pages - on_ends + 1, num_pages + 1)
    else:
        yield from range(number + 1, num_pages + 1)
