from .reader import read_varint, read_binary_uint8, read_binary_int32
from .writer import write_varint, write_binary_uint8, write_binary_int32


class BlockInfo(object):
    is_overflows = False
    bucket_num = -1

    def write(self, buf):
        # Set of pairs (`FIELD_NUM`, value) in binary form. Then 0.
        write_varint(1, buf)
        write_binary_uint8(self.is_overflows, buf)

        write_varint(2, buf)
        write_binary_int32(self.bucket_num, buf)

        write_varint(0, buf)

    def read(self, buf):
        while True:
            field_num = read_varint(buf)
            if not field_num:
                break

            if field_num == 1:
                self.is_overflows = bool(read_binary_uint8(buf))

            elif field_num == 2:
                self.bucket_num = read_binary_int32(buf)


class Block(object):
    def __init__(self, columns_with_types=None, data=None, info=None,
                 check_sanity=False):
        self.columns_with_types = columns_with_types or []
        self.data = data or []

        # Transpose data rows->columns
        if data:
            # Guessing about whole data format by first row.
            # Converting dicts to lists.
            columns = [x[0] for x in self.columns_with_types]
            if isinstance(data[0], dict):
                data = [tuple(row[c] for c in columns) for row in data]

            if check_sanity:
                # For checking that each row has the same length.
                first_row_len = len(data[0])
                first_j = first_row_len - 1

                columns_expected = len(columns_with_types)
                if columns_expected != first_row_len:
                    msg = 'Expected {} columns, got {}'.format(
                        columns_expected, first_row_len)
                    raise ValueError(msg)

            self.data = [[None] * len(data) for row in data[0]]
            for i, row in enumerate(data):
                j = 0
                for j, x in enumerate(row):
                    self.data[j][i] = x

                if check_sanity and j != first_j:
                    raise ValueError('Different rows length')

            self.data = [tuple(x) for x in self.data]

        self.info = info or BlockInfo()

        super(Block, self).__init__()

    @property
    def columns(self):
        return len(self.data)

    @property
    def rows(self):
        return len(self.data[0]) if self.columns else 0
