from dataclasses import dataclass
from threading import Thread, Lock, Semaphore
from time import sleep

@dataclass(frozen=True)
class Order:
    product: str
    quantity: int

class OrderProcessor:
    def __init__(self, n_threads: int = 1, use_lock: bool = True, use_semaphore: bool = False, prefix: str = "", sufix: str = ""):
        if n_threads < 1:
            raise ValueError("n_threads debe ser mayor o igual a 1")
        self._use_lock = use_lock
        self._use_semaphore = use_semaphore
        self._prefix = prefix
        self._sufix = sufix
        self._n_threads = n_threads
        self.inventory = {"ProductoA": 10, "ProductoB": 2}  # Aqui va el inventario de las cosas que tenemos!
        self.lock = Lock()
        self.semaphore = Semaphore(self._n_threads)
        
    def process_orders(self, orders: list[Order]):
        threads = []
        for order in orders:
            thread = Thread(target=self._process_order, args=(order,))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
            
    def _process_order(self, order: Order):
        msg_dict = {
            "msg_start": f"{self._prefix} Empezado pedido: {order.quantity} x {order.product} {self._sufix}",
            "msg_final": f"{self._prefix} Procesado pedido: {order.quantity} x {order.product} {self._sufix}",
            "msg_not_found": f"{self._prefix} Pedido no encontrado: {order.product} {self._sufix}"
        }
        if self._use_lock:
            with self.lock:
                self._update_inventory(order, msg_dict)
        elif self._use_semaphore:
            with self.semaphore:
                self._update_inventory(order, msg_dict)
        else:
            self._update_inventory(order, msg_dict)
            
    def _update_inventory(self, order: Order, msg_dict: dict[str, str]):
        product, quantity = order.product, order.quantity
        print(msg_dict["msg_start"])
        sleep(3)
        if product in self.inventory:
            if quantity > self.inventory[product]:
                print(f"{self._prefix} Pedido sin tantas existencias: {quantity} x {product} {self._sufix}")
            else:
                self.inventory[product] -= quantity
                print(msg_dict["msg_final"])
        else:
            print(msg_dict["msg_not_found"])
        
class OrderProcessorBuilder:
    def __init__(self):
        self._processor = OrderProcessor()
        
    def threads(self, number_threads: int):
        if number_threads < 1:
            raise ValueError("number_threads debe ser mayor o igual a 1")
        self._processor._n_threads = number_threads
        self._processor.semaphore = Semaphore(number_threads)
        return self
    
    def use_lock(self, flag: bool):
        self._processor._use_lock = flag
        if flag:
            self._processor._use_semaphore = False
        return self
    
    def use_semaphore(self, flag: bool):
        self._processor._use_semaphore = flag
        if flag:
            self._processor._use_lock = False
        return self
    
    def prefix(self, string: str):
        self._processor._prefix = string
        return self
    
    def sufix(self, string: str):
        self._processor._sufix = string
        return self
    
    def build(self) -> OrderProcessor:
        return self._processor

ordenes = [
    Order("ProductoA", 3),
    Order("ProductoB", 2),
    Order("ProductoA", 1),
    Order("ProductoC", 1),
    Order("ProductoD", 1),
    Order("ProductoB", 10)
]

processor = OrderProcessorBuilder().threads(2).use_semaphore(True).prefix("[INICIO]").sufix("[FINAL]").build()
print(processor.inventory)
processor.process_orders(ordenes)
print(processor.inventory)