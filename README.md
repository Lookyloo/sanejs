# sanejs

Use CDNJS as a source to build hashes of known JS/CSS/IMG/... content used all over the internet

# Big warning. Seriously.

1. Pulling the submodule downloads a ~7G git repository
2. At first checkout, it will use ~180G on your disk

You've been warned.

# Online service for sanejs

If you don't want to install the complete server, CIRCL operates an online service (https://sanejs.circl.lu) to query sanejs.

## sanejs - online service

```bash
curl https://sanejs.circl.lu/ --request POST --data '{"sha512":"908a25a227d1d6dd4397ddbf8ed19d58d092edd11f7dfbe89385e1f340211aed0ef7777edae3d3c1824f410949b7b9373753b83a3178b0f656fb97424bb20bc2"}'
```

```bash
curl https://sanejs.circl.lu/library --request POST --data '{"library":"dojo"}'

# Installation

**IMPORTANT**: Use [pipenv](https://pipenv.readthedocs.io/en/latest/)

**NOTE**: Yes, it requires python3.6+. No, it will never support anything older.

## Install redis

```bash
git clone https://github.com/antirez/redis.git
cd redis
git checkout 5.0
make
make test
cd ..
```

## Install & run SaneJS

```bash
git clone https://github.com/CIRCL/sanejs.git
cd sanejs
git submodule init
git submodule update
pushd cdnjs
git checkout master
popd
pipenv install
echo SANEJS_HOME="'`pwd`'" > .env
pipenv shell
# Starts all the backend
start.py
# Start the web interface
start_website.py
```

**Note**: As long as the hashes aren't loaded, every query will return the following:

```json
{
  "error": "The hashes are not all loaded yet, try again later."
}
```

When they're all loaded, the repository will be pulled on a regular basis and load the new hashes.

# Curl Usage

```bash
curl https://sanejs.circl.lu/ --request POST --data '{"sha512":"908a25a227d1d6dd4397ddbf8ed19d58d092edd11f7dfbe89385e1f340211aed0ef7777edae3d3c1824f410949b7b9373753b83a3178b0f656fb97424bb20bc2"}'
```

```bash
curl https://sanejs.circl.lu/library --request POST --data '{"library":"dojo"}'
```

# CLI usage (from PySaneJS, the submodule in ./client/)

It is not super useful to use it like that, but you can give it a try:

```bash
# You can pass a list of sha512
sanejs --url http://0.0.0.0:5007 --sha512 908a25a227d1d6dd4397ddbf8ed19d58d092edd11f7dfbe89385e1f340211aed0ef7777edae3d3c1824f410949b7b9373753b83a3178b0f656fb97424bb20bc2
```

```json
{
  "response": [
    "dojo|1.11.0-rc3|resources/dnd.css",
    "dojo|1.9.3|resources/dnd.css",
    "dojo|1.8.10|resources/dnd.css",
    "dojo|1.10.0|resources/dnd.css",
    "dojo|1.9.1|resources/dnd.css",
    "dojo|1.10.2|resources/dnd.css",
    "dojo|1.9.7|resources/dnd.css",
    "dojo|1.8.9|resources/dnd.css",
    "dojo|1.10.1|resources/dnd.css",
    "dojo|1.11.0-rc4|resources/dnd.css",
    "dojo|1.8.2|resources/dnd.css",
    "dojo|1.10.4|resources/dnd.css",
    "dojo|1.8.8|resources/dnd.css",
    "dojo|1.9.6|resources/dnd.css",
    "dojo|1.8.0|resources/dnd.css",
    "dojo|1.11.0-rc5|resources/dnd.css",
    "dojo|1.8.6|resources/dnd.css",
    "dojo|1.9.5|resources/dnd.css",
    "dojo|1.8.1|resources/dnd.css",
    "dojo|1.10.3|resources/dnd.css",
    "dojo|1.8.5|resources/dnd.css",
    "dojo|1.8.3|resources/dnd.css",
    "dojo|1.9.4|resources/dnd.css",
    "dojo|1.9.0|resources/dnd.css",
    "dojo|1.9.2|resources/dnd.css",
    "dojo|1.11.0-rc1|resources/dnd.css",
    "dojo|1.8.4|resources/dnd.css",
    "dojo|1.8.7|resources/dnd.css",
    "dojo|1.11.0-rc2|resources/dnd.css"
  ]
}
```


```bash
sanejs --url http://0.0.0.0:5007 --library jquery-tools  # You can pass a list of tools
```

```json
{
  "response": {
    "jquery-tools": {
      "1.2.0": {
        "jquery.tools.min.js": "f95c034c328d7c3f5bd14e0fd82a9309ab197931ff41120ca8d749036f5a773092dc0f357b190570754f5a17d7a42a71b932793a54b0ec812eef3730ddc93dc9"
      },
      "1.2.1": {
        "jquery.tools.min.js": "ba386f0827c971277c3f6941c58f9dbc410f668b272201127ee38377f57a8ec37c2cb415089cb12205c6ed2c339bf6f5a7d20c6259ae1f55337154257a398204"
      },
      "1.2.2": {
        "jquery.tools.min.js": "b40b56d553cb23c7fb607f31118ba7c2ae1058308795d5b0f6d42025c7aa3f9f2b5fbb3be4c8734cf6f8f2c3dd202aca79de14d7a54d448bbe34c8198b94fc96"
      },
      "1.2.3": {
        "jquery.tools.min.js": "597bb3566588ba0ec2c7fce0f4449022be687878d5c04113526503a0e77b79755c33a9ba1ad6ef8232a4a51b98b7a8b287caba7db699b4374a53370fb51f859d"
      },
      "1.2.4": {
        "jquery.tools.min.js": "1dbcb177bf7b28c72d3b54aa71befa5a6d91e35c1df702a1991c9df7e60aa3efcd59bbdb8fb0a61326c3ebfe046c809ea01030c3fd8de4b90668e2aee778d968"
      },
      "1.2.5": {
        "jquery.tools.min.js": "d91fdfc6cb7529493182d3c7ea12eb6cb3323060434bfd4c98c95c9f223fa97cff9a9254c5655b51818491d9de9f53ba3df1b5cbd1a20ed0dce683829b75db6a"
      },
      "1.2.6": {
        "jquery.tools.min.js": "f8be2202d8ff862849e19562ba93e2743027298d9fc908191ca48978458a7053c584c581f44f37b8a595ce9262fbda1b5bea83330dd3366fc2c44a172e286f96"
      },
      "1.2.7": {
        "jquery.tools.min.js": "b15d794a0289980a2dcffe70eb5ecaf42e2a3785a3dd8324f577fae7e8f381098fa9f8f048f6f0c1029d584d618ff5a30c6112a9baa1e1809f2ffb4781373e11"
      }
    }
  }
}
```
