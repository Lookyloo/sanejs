# sanejs
Use CDNJS as a source to build hashes of known JS/CSS/IMG/... content used all over the internet

# Big warning. Seriously.

1. Pulling the submodule downloads a ~7G git repository
2. At first checkout, it will use ~140G on your disk

You've been warned.

# Initializing

```bash
pip install -r requirements.txt
./init_cdnjs.sh  # Takes 3 hours
./build_hashes.py  # Takes 1 hour
```
Now, you have `lookup.json` which has this format:

```json

{
    '<sha521>': [
        {
            "libname": "library name",
            "version": "version",
            "filename": "file with that hash in the library"
        },
        {
            <other file with the same hash>
        }
    ]
}

```

# (dummy) Usage

It is stupid to use it like that, but you can give it a try:

```bash
./search.sh -s <SHA512>
```

# Actual Usecase

It will be used in [Lookyloo](https://github.com/CIRCL/lookyloo) to mark known good content.

