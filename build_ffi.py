import os
from pathlib import Path
from cffi import FFI


lib_dir = Path(os.getcwd()) / "lib"
ffibuilder = FFI()
ffibuilder.cdef("""
typedef   signed char		   ma_int8;
typedef unsigned char		   ma_uint8;
typedef   signed short		  ma_int16;
typedef unsigned short		  ma_uint16;
typedef   signed int			ma_int32;
typedef unsigned int			ma_uint32;
typedef   signed long long  ma_int64;
typedef unsigned long long  ma_uint64;
typedef ma_uint64		   ma_uintptr;
typedef ma_uint8	ma_bool8;
typedef ma_uint32   ma_bool32;

#define MA_TRUE	 1
#define MA_FALSE	0
#define MA_MIN_CHANNELS				 1
#define MA_MAX_CHANNELS				 254

typedef enum
{
	MA_LOG_LEVEL_DEBUG   = 4,
	MA_LOG_LEVEL_INFO	= 3,
	MA_LOG_LEVEL_WARNING = 2,
	MA_LOG_LEVEL_ERROR   = 1
} ma_log_level;

typedef enum
{
	MA_SUCCESS						=  0,
	MA_ERROR						  = -1,  /* A generic error. */
	MA_INVALID_ARGS				   = -2,
	MA_INVALID_OPERATION			  = -3,
	MA_OUT_OF_MEMORY				  = -4,
	MA_OUT_OF_RANGE				   = -5,
	MA_ACCESS_DENIED				  = -6,
	MA_DOES_NOT_EXIST				 = -7,
	MA_ALREADY_EXISTS				 = -8,
	MA_TOO_MANY_OPEN_FILES			= -9,
	MA_INVALID_FILE				   = -10,
	MA_TOO_BIG						= -11,
	MA_PATH_TOO_LONG				  = -12,
	MA_NAME_TOO_LONG				  = -13,
	MA_NOT_DIRECTORY				  = -14,
	MA_IS_DIRECTORY				   = -15,
	MA_DIRECTORY_NOT_EMPTY			= -16,
	MA_AT_END						 = -17,
	MA_NO_SPACE					   = -18,
	MA_BUSY						   = -19,
	MA_IO_ERROR					   = -20,
	MA_INTERRUPT					  = -21,
	MA_UNAVAILABLE					= -22,
	MA_ALREADY_IN_USE				 = -23,
	MA_BAD_ADDRESS					= -24,
	MA_BAD_SEEK					   = -25,
	MA_BAD_PIPE					   = -26,
	MA_DEADLOCK					   = -27,
	MA_TOO_MANY_LINKS				 = -28,
	MA_NOT_IMPLEMENTED				= -29,
	MA_NO_MESSAGE					 = -30,
	MA_BAD_MESSAGE					= -31,
	MA_NO_DATA_AVAILABLE			  = -32,
	MA_INVALID_DATA				   = -33,
	MA_TIMEOUT						= -34,
	MA_NO_NETWORK					 = -35,
	MA_NOT_UNIQUE					 = -36,
	MA_NOT_SOCKET					 = -37,
	MA_NO_ADDRESS					 = -38,
	MA_BAD_PROTOCOL				   = -39,
	MA_PROTOCOL_UNAVAILABLE		   = -40,
	MA_PROTOCOL_NOT_SUPPORTED		 = -41,
	MA_PROTOCOL_FAMILY_NOT_SUPPORTED  = -42,
	MA_ADDRESS_FAMILY_NOT_SUPPORTED   = -43,
	MA_SOCKET_NOT_SUPPORTED		   = -44,
	MA_CONNECTION_RESET			   = -45,
	MA_ALREADY_CONNECTED			  = -46,
	MA_NOT_CONNECTED				  = -47,
	MA_CONNECTION_REFUSED			 = -48,
	MA_NO_HOST						= -49,
	MA_IN_PROGRESS					= -50,
	MA_CANCELLED					  = -51,
	MA_MEMORY_ALREADY_MAPPED		  = -52,

	/* General non-standard errors. */
	MA_CRC_MISMATCH				   = -100,

	/* General miniaudio-specific errors. */
	MA_FORMAT_NOT_SUPPORTED		   = -200,
	MA_DEVICE_TYPE_NOT_SUPPORTED	  = -201,
	MA_SHARE_MODE_NOT_SUPPORTED	   = -202,
	MA_NO_BACKEND					 = -203,
	MA_NO_DEVICE					  = -204,
	MA_API_NOT_FOUND				  = -205,
	MA_INVALID_DEVICE_CONFIG		  = -206,
	MA_LOOP						   = -207,
	MA_BACKEND_NOT_ENABLED			= -208,

	/* State errors. */
	MA_DEVICE_NOT_INITIALIZED		 = -300,
	MA_DEVICE_ALREADY_INITIALIZED	 = -301,
	MA_DEVICE_NOT_STARTED			 = -302,
	MA_DEVICE_NOT_STOPPED			 = -303,

	/* Operation errors. */
	MA_FAILED_TO_INIT_BACKEND		 = -400,
	MA_FAILED_TO_OPEN_BACKEND_DEVICE  = -401,
	MA_FAILED_TO_START_BACKEND_DEVICE = -402,
	MA_FAILED_TO_STOP_BACKEND_DEVICE  = -403
} ma_result;

typedef enum
{
	/* Resource manager flags. */
	MA_SOUND_FLAG_STREAM				= 0x00000001,   /* MA_RESOURCE_MANAGER_DATA_SOURCE_FLAG_STREAM */
	MA_SOUND_FLAG_DECODE				= 0x00000002,   /* MA_RESOURCE_MANAGER_DATA_SOURCE_FLAG_DECODE */
	MA_SOUND_FLAG_ASYNC				 = 0x00000004,   /* MA_RESOURCE_MANAGER_DATA_SOURCE_FLAG_ASYNC */
	MA_SOUND_FLAG_WAIT_INIT			 = 0x00000008,   /* MA_RESOURCE_MANAGER_DATA_SOURCE_FLAG_WAIT_INIT */
	MA_SOUND_FLAG_UNKNOWN_LENGTH		= 0x00000010,   /* MA_RESOURCE_MANAGER_DATA_SOURCE_FLAG_UNKNOWN_LENGTH */
	MA_SOUND_FLAG_LOOPING			   = 0x00000020,   /* MA_RESOURCE_MANAGER_DATA_SOURCE_FLAG_LOOPING */

	/* ma_sound specific flags. */
	MA_SOUND_FLAG_NO_DEFAULT_ATTACHMENT = 0x00001000,   /* Do not attach to the endpoint by default. Useful for when setting up nodes in a complex graph system. */
	MA_SOUND_FLAG_NO_PITCH			  = 0x00002000,   /* Disable pitch shifting with ma_sound_set_pitch() and ma_sound_group_set_pitch(). This is an optimization. */
	MA_SOUND_FLAG_NO_SPATIALIZATION	 = 0x00004000	/* Disable spatialization. */
} ma_sound_flags;

typedef struct ma_node_base ma_node_base;
typedef struct ma_node_graph ma_node_graph;
typedef struct ma_context ma_context;
typedef struct ma_device ma_device;
typedef struct ma_engine ma_engine;
typedef struct ma_sound  ma_sound;
typedef ma_sound        ma_sound_group;

struct ma_node_base
{
	ma_node_graph* pNodeGraph;
	...;
};

struct ma_node_graph
{
	ma_node_base base;
	...;
};


struct ma_context
{
	...;
};

struct ma_engine
{
	ma_node_graph nodeGraph;
	...;
};

typedef struct
{
	ma_node_base baseNode;
	...;
} ma_engine_node;

struct ma_sound
{
	ma_engine_node engineNode;
	...;
};

typedef struct
{
	...;
} ma_engine_config;


ma_result ma_engine_init(const ma_engine_config* pConfig, ma_engine* pEngine);
void ma_engine_uninit(ma_engine* pEngine);
ma_result ma_engine_read_pcm_frames(ma_engine* pEngine, void* pFramesOut, ma_uint64 frameCount, ma_uint64* pFramesRead);
ma_node_graph* ma_engine_get_node_graph(ma_engine* pEngine);
ma_result ma_engine_play_sound(ma_engine* pEngine, const char* pFilePath, ma_sound_group* pGroup);
""")

ffibuilder.set_source("_c_miniaudio", """
	#include <stdint.h>
	#include <stdlib.h>
	#define MINIAUDIO_IMPLEMENTATION
	#include "lib/miniaudio.h"
""",
	include_dirs=[lib_dir]
)

ffibuilder.compile(verbose=True)
