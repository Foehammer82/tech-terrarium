import inspect

from pydantic import BaseModel


class Foo(BaseModel):
    bar: str = "test"


if __name__ == "__main__":
    print(isinstance(Foo, BaseModel))
    print(inspect.isclass(Foo) and issubclass(Foo, BaseModel))

    foo = Foo(bar="test")
    print(isinstance(foo, BaseModel))
    print(inspect.isclass(foo) and issubclass(foo, BaseModel))
