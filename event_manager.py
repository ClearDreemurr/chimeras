_listeners = {}

def register(event_type, callback):
    """注册某个事件类型的监听器"""
    if event_type not in _listeners:
        _listeners[event_type] = []
    _listeners[event_type].append(callback)

def publish(event_type, **kwargs):
    """发布事件，将数据传递给所有监听器"""
    if event_type in _listeners:
        for callback in _listeners[event_type]:
            callback(**kwargs)
