sed -i '/def _parse_file_data(/,/^    raise UnsupportedBinaryError/c\
def _parse_file_data(self, filename, filedata):\
    import io\
        import lief\
            if isinstance(filedata, (bytes, bytearray)):\\
                    filedata = io.BytesIO(filedata)\
                        parsed_file = self.os_plugins.parse(filename, filedata)\
                            if parsed_file is None:\\
                                    raise UnsupportedBinaryError(f"{filename} is unsupported file format")\
                                        return parsed_file' /opt/conda/envs/myenv/lib/python3.10/site-packages/zelos/engine.py