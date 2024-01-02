def query_one_page(query, page, size):
    offset = (page - 1) * int(size)
    return (
        query.offset(offset if offset > 0 else 0).limit(size if size > 0 else 0).all()
    )
