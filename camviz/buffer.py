
import numpy as np
from OpenGL.GL import \
    glGenBuffers, glBindBuffer, glBufferData, glBufferSubData, glClearBufferfi, \
    GL_ARRAY_BUFFER, GL_STATIC_DRAW
from camviz.utils.types import is_tup, is_lst, is_tct
from camviz.utils.utils import numpyf, cmapJET


class Buffer:

    def __init__(self, data, dtype, gltype):

        self.id, self.max = glGenBuffers(1), 0
        self.dtype, self.gltype = dtype, gltype

        if is_tup(data):
            data, (self.n, self.d) = None, data
        else:
            data = self.process(data)
            self.n, self.d = data.shape[:2]

        if self.n > self.max:
            self._create(data)

    @property
    def size(self):
        return self.n * self.d * np.dtype(self.dtype).itemsize

    def process(self, data):
        if is_lst(data):
            data = numpyf(data)
        if is_tct(data):
            data = data.detach().cpu().numpy()
        if data.dtype != self.dtype:
            data = data.astype(self.dtype)
        if len(data.shape) == 1:
            data = np.expand_dims(data, 1)
        return data

    def _create(self, data):
        self.max = self.n
        glBindBuffer(GL_ARRAY_BUFFER, self.id)
        glBufferData(GL_ARRAY_BUFFER, self.size, data, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def update(self, data):

        data = self.process(data)
        self.n = 0 if data.size == 0 else data.shape[0]

        if self.n > self.max:
            self._create(data)
        else:
            glBindBuffer(GL_ARRAY_BUFFER, self.id)
            glBufferSubData(GL_ARRAY_BUFFER, 0, self.size, data.astype(self.dtype))
            glBindBuffer(GL_ARRAY_BUFFER, 0)

    def clear(self):
        self.n = 0

    def updateJET(self, data):
        self.update(cmapJET(data))

# class BufferData(Buffer):
#     def __init__(self, data):
#         super(BufferData, self).__init__(data, np.float32, GL_FLOAT)
#
#
# class bufferIDX(Buffer):
#     def __init__(self, data):
#         super(bufferIDX, self).__init__(data, np.uint32, GL_UNSIGNED_INT)
#
#
# class BufferData2(BufferData):
#     def __init__(self, data):
#         super(BufferData2, self).__init__((data, 2))
#
#
# class BufferData3(BufferData):
#     def __init__(self, data):
#         super(BufferData3, self).__init__((data, 3))
#
