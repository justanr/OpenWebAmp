from slugify import Slugify

slugger = Slugify(
    to_lower=True,
    max_length=50,
    separator='+'
    )
