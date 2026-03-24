# def gen():
#     x = 1
#     while True:
#         received = yield x
#         if received:
#             x = received
#         else:
#             x += 1
# g = gen()
# print(next(g), g.send(10), next(g), g.send(None))

# class Strategy:
#     def execute(self, x):
#         raise NotImplementedError
    
# class AddOne(Strategy):
#     def execute(self, x): return x + 1
    
# class Multiply(Strategy):
#     def execute(self, x):
#         return x *2
    
# class Context:
#     def __init__(self, strategy: Strategy):
#         self.strategy = strategy
#     def run(self, x):
#         return self.strategy.execute(x)
    
# ctx = Context(AddOne())
# result1 = ctx.run(3)

# ctx.strategy = Multiply()
# result2 = ctx.run(result1)

# print(result2)

# class Builder:
#     def __init__(self):
#         self.product = []
        
#     def add_a(self):
#         self.product.append("A")
#         return self
    
#     def add_b(self):
#         self.product.append("B")
#         return self
    
#     def add_many(self, items):
#         self.product.extend(items)
#         return self
    
#     def conditional_add(self, flag):
#         if flag:
#             self.product.append("X")
#         return self
    
#     def reset(self):
#         self.product = []
#         return self
    
#     def build(self):
#         return self.product

# b = Builder()
# p1 = b.add_a().add_b().build()
# p2 = b.add_many(["C", "D"]).build()
# p3 = b.reset().add_a().conditional_add(True).build()

# print(p1, p2, p3)

# def counter(func):
#     count = 0
#     def wrapper(*args):
#         nonlocal count
#         count += 1
#         return func(*args) + count
#     return wrapper

# @counter
# def f(x):
#     return x

# print(f(1), f(1), f(1))

# import threading

# counter = 0
# lock = threading.Lock()

# def work():
#     global counter
#     for _ in range(100000):
#         lock.acquire()
#         counter += 1
#         lock.release()
        
# threads = [threading.Thread(target=work) for _ in range(2)]

# for t in threads:
#     t.start()
# for t in threads:
#     t.join()

# print(counter)

# class MySQLDatabase:
#     def connect(self):
#         return "mysql"
# class PostgresDatabase:
#     def connect(self):
#         return "postgres"
# class Service:
#     def __init__(self):
#         self.db = MySQLDatabase()
        
#     def process(self, use_pg=False):
#         if use_pg:
#             self.db = PostgresDatabase()
#         return self.db.connect()
    
# s = Service()
# print(s.process(), s.process(True))

# def get_list():
#     return []
# def test_list():
#     l = get_list()
#     l.append(1)
#     assert 1 == get_list()

# class Weird:
#     def __init__(self):
#         self.data = {}
        
#     def __getitem__ (self, key): 
#         return self.data.get(key, 0) + 1
    
#     def __setitem__ (self, key, value): 
#         self.data[key] = value * 2
        
#     def __delitem__ (self, key):
#         if key in self.data: 
#             del self.data[key]

# w = Weird()
# w["a"] = 3
# x = w["a"]
# del w["a"]
# y = w["a"]
# print(x, y)

# from abc import ABC, abstractmethod

# class Base(ABC):
#     @property
#     @abstractmethod
#     def value(self): pass
#     def compute(self):
#         return self.value + 5

# class Child(Base):
#     def __init__(self): self._v = 10

#     @property
#     def value(self):
#         return self._v * 2

# c = Child()
# print(c.compute())

# class A:
#     factor = 2

#     @classmethod
#     def create(cls, x):
#         return cls(x * cls.factor)
    
#     def __init__(self, v):
#         self.v = v

# class B(A):
#     factor = 3
    
# b = B.create(2)
# print(b.v, isinstance(b, B))