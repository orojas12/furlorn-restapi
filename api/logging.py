from logging.handlers import MemoryHandler


class EventMemoryHandler(MemoryHandler):
    """
    A handler class that behaves similarly to MemoryHandler, except that it
    flushes records in the buffer only when an event of a certain severity
    or greater is seen.
    """

    def emit(self, record):
        """
        Emit a record.

        If capacity is reached, discard first record in the buffer
        before appending the record. If shouldFlush() tells us to,
        call flush() to process the buffer.
        """
        if len(self.buffer) == self.capacity:
            self.buffer.pop(0)
        self.buffer.append(record)
        if self.shouldFlush(record):
            self.flush()

    def shouldFlush(self, record):
        """
        Check for a record at the flushLevel or higher.
        """
        return record.levelno >= self.flushLevel
