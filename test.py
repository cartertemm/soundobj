from _c_miniaudio import ffi, lib


engine = ffi.new("ma_engine*")
result = lib.ma_engine_init(ffi.NULL, engine)
print(result)
lib.ma_engine_play_sound(engine, ffi.new("char[]", b"test.wav"), ffi.NULL)
input("Enter to stop")
lib.ma_engine_uninit(engine)
