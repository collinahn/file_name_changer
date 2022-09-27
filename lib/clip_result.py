import clipboard


class ClipSave:
    @classmethod
    def to_clipboard(cls, chunk: list, sep: str = '\n') -> bool:
        if not chunk:
            return False
        msg = sep.join((str(element) for element in chunk))
        print(repr(msg))
        clipboard.copy(msg)
        return True


if __name__ == '__main__':

    ClipSave.to_clipboard([ClipSave, 'str2', 'str3', 'str4'])
    ClipSave.to_clipboard([])
