import threading
class Barrier:
  def __init__(self, n):
    self.n = n 
    self.count = 0
    self.mutex = threading.Semaphore(1)
    self.barrier = threading.Semaphore(0)

  def wait(self):
    self.mutex.acquire()
    self.count += 1
    self.mutex.release()
    if self.count == self.n:
      self.count = 0
      self.barrier.release()
    self.barrier.acquire()
    self.barrier.release()