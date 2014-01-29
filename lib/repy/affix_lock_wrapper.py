class affix_lock_wrapper:
  """
  <Purpose>
    This function should be used as a locking mechanism for affixs.
    It is used to ensure that socket operations such as send(),
    recv() and close() occur atomically without interference.
    Most affixs should use this as a decorator for their socket
    operations. The decorator takes in an argument which is used
    as the lock name. Each individual affix should use their own
    lockname and share that lock among all its call (unless otherwise
    necessary).

    An example usage would be:
      
      i = 0   

      @affix_lock_wrapper("hello_world")
      def foo():
        global i
        print i
        i += 1


    If the function foo() is threaded, i should still increment properly 
    without any contention.   
  """

  lock_dict = {}

  # Initialize the lock, if it is a new lock.
  def __init__(self, lockname):

    if lockname not in self.lock_dict.keys():
      self.lock_dict[lockname] = createlock()

    self._lockname = lockname
       

  def __call__(self, target_func):
    
    # The wrapper function acquires the appropriate lock before
    # calling the function.
    def wrapper(*args, **kwargs):
      self.lock_dict[self._lockname].acquire(True)

      try:
        target_func(*args, **kwargs)
      finally:
        self.lock_dict[self._lockname].release()

    return wrapper    
