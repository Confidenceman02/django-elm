# Djelm flags

## What are they?

Flags are how we map python values from our django server to Elm primitives that our programs will be initiated with.

You can think of them as a schema of sorts, that can do a number of extra tasks for us, such as:

- Validate python values
- Generate Elm decoders

You can find a good explanation for djelm flags with examples in the official guide [here](https://github.com/Confidenceman02/django-elm?tab=readme-ov-file#flags).

# StringFlag

### Args

literal : str

```python
StringFlag()

# Match against a literal string

StringFlag(literal="hello")
```

```
# python
"foo" : str

# elm
"foo" : String
```

# IntFlag

```python
IntFlag()
```

```
# python
2 : int

# elm
2 : Int
```

# FloatFlag

```python
FloatFlag()
```

```
# python
2.0 : float

# elm
2.0 : Float
```

# BoolFlag

```python
BoolFlag()
```

```
# python
True : bool

# elm
True : Bool
```

# NullableFlag

argument: Flag

```python
NullableFlag(StringFlag())
```

```
# python
None : str | None

# elm
Nothing : Maybe String

# python
"foo" : str | None

# elm
Just "foo" : Maybe String
```

# ListFlag

argument: Flag

```python
ListFlag(StringFlag())
```

```
# python
["foo"] : list[str]

# elm
["foo"] : List String
```

# ObjectFlag

argument: dict[str, Flag]

```python
ObjectFlag({"hello": StringFlag()})
```

```
# python
{"hello": "world"} : dict[str, str]

# elm
{ hello = "world" } : { hello : String }
```

# CustomTypeFlag

Elm calls these custom types, but you may also know them as the following:

- Discriminated unions
- Tagged unions
- Sum types
- Algebraic data types

argument: list[tuple[str, Flag]]

```python
CustomTypeFlag(variants=[("A", StringFlag()), ("B", IntFlag())])
```

```
# python
"hello" : Union[str, int]
2       : Union[str, int]

# elm
A "hello" : Custom
B 2       : Custom
```
