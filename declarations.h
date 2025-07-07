/*
* SoundObj declarations
*
* This code is never included in a script or compiled directly.
* Instead, it is read by the FFI builder and constructs the function and type definitions that we use to make soundobj work correctly.
*/

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
typedef unsigned short wchar_t;
typedef ma_uint64 size_t;

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
typedef ma_sound		ma_sound_group;

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

typedef struct
{
	...;
} ma_engine_node_config;

typedef struct
{
	float x;
	float y;
	float z;
} ma_vec3f;

typedef enum
{
	ma_format_unknown = 0,
	ma_format_u8	  = 1,
	ma_format_s16	 = 2,
	ma_format_s24	 = 3,
	ma_format_s32	 = 4,
	ma_format_f32	 = 5,
	ma_format_count
} ma_format;

typedef enum
{
	ma_pan_mode_balance = 0,
	ma_pan_mode_pan
} ma_pan_mode;

typedef enum
{
	ma_attenuation_model_none,
	ma_attenuation_model_inverse,
	ma_attenuation_model_linear,
	ma_attenuation_model_exponential
} ma_attenuation_model;

typedef enum
{
	ma_positioning_absolute,
	ma_positioning_relative
} ma_positioning;

typedef enum
{
	ma_engine_node_type_sound,
	ma_engine_node_type_group
} ma_engine_node_type;

typedef void (* ma_sound_end_proc)(void* pUserData, ma_sound* pSound);

typedef struct
{
	ma_uint32 counter;
	...;
} ma_fence;

typedef void ma_data_source;
typedef struct ma_resource_manager ma_resource_manager;
typedef struct ma_log ma_log;
typedef void ma_node;
typedef ma_uint8 ma_channel;
typedef ma_uint32 ma_spinlock;

#define MA_CHANNEL_NONE			   0
#define MA_CHANNEL_MONO			   1
#define MA_CHANNEL_FRONT_LEFT		 2
#define MA_CHANNEL_FRONT_RIGHT		3
#define MA_CHANNEL_FRONT_CENTER	   4
#define MA_CHANNEL_LFE				5
#define MA_CHANNEL_BACK_LEFT		  6
#define MA_CHANNEL_BACK_RIGHT		 7
#define MA_CHANNEL_FRONT_LEFT_CENTER  8
#define MA_CHANNEL_FRONT_RIGHT_CENTER 9
#define MA_CHANNEL_BACK_CENTER		10
#define MA_CHANNEL_SIDE_LEFT		  11
#define MA_CHANNEL_SIDE_RIGHT		 12
#define MA_CHANNEL_TOP_CENTER		 13
#define MA_CHANNEL_TOP_FRONT_LEFT	 14
#define MA_CHANNEL_TOP_FRONT_CENTER   15
#define MA_CHANNEL_TOP_FRONT_RIGHT	16
#define MA_CHANNEL_TOP_BACK_LEFT	  17
#define MA_CHANNEL_TOP_BACK_CENTER	18
#define MA_CHANNEL_TOP_BACK_RIGHT	 19
#define MA_CHANNEL_AUX_0			  20

typedef ma_uint8 ma_channel_position;

typedef struct
{
	void* pUserData;
	void* (* onMalloc)(size_t sz, void* pUserData);
	void* (* onRealloc)(void* p, size_t sz, void* pUserData);
	void  (* onFree)(void* p, void* pUserData);
} ma_allocation_callbacks;

typedef struct
{
	...;
} ma_sound_config;

typedef struct
{
	...;
} ma_sound_group_config;

ma_engine_config ma_engine_config_init(void);
ma_result ma_engine_init(const ma_engine_config* pConfig, ma_engine* pEngine);
void ma_engine_uninit(ma_engine* pEngine);
ma_result ma_engine_read_pcm_frames(ma_engine* pEngine, void* pFramesOut, ma_uint64 frameCount, ma_uint64* pFramesRead);
ma_node_graph* ma_engine_get_node_graph(ma_engine* pEngine);
ma_resource_manager* ma_engine_get_resource_manager(ma_engine* pEngine);
ma_device* ma_engine_get_device(ma_engine* pEngine);
ma_log* ma_engine_get_log(ma_engine* pEngine);
ma_node* ma_engine_get_endpoint(ma_engine* pEngine);
ma_uint32 ma_engine_get_channels(const ma_engine* pEngine);
ma_uint32 ma_engine_get_sample_rate(const ma_engine* pEngine);
ma_uint64 ma_engine_get_time_in_pcm_frames(const ma_engine* pEngine);
ma_uint64 ma_engine_get_time_in_milliseconds(const ma_engine* pEngine);
ma_result ma_engine_set_time_in_pcm_frames(ma_engine* pEngine, ma_uint64 globalTime);
ma_result ma_engine_set_time_in_milliseconds(ma_engine* pEngine, ma_uint64 globalTime);
ma_uint64 ma_engine_get_time(const ma_engine* pEngine);
ma_result ma_engine_set_time(ma_engine* pEngine, ma_uint64 globalTime);
ma_result ma_engine_start(ma_engine* pEngine);
ma_result ma_engine_stop(ma_engine* pEngine);
ma_result ma_engine_set_volume(ma_engine* pEngine, float volume);
float ma_engine_get_volume(ma_engine* pEngine);
ma_result ma_engine_set_gain_db(ma_engine* pEngine, float gainDB);
float ma_engine_get_gain_db(ma_engine* pEngine);
ma_uint32 ma_engine_get_listener_count(const ma_engine* pEngine);
ma_uint32 ma_engine_find_closest_listener(const ma_engine* pEngine, float absolutePosX, float absolutePosY, float absolutePosZ);
void ma_engine_listener_set_position(ma_engine* pEngine, ma_uint32 listenerIndex, float x, float y, float z);
ma_vec3f ma_engine_listener_get_position(const ma_engine* pEngine, ma_uint32 listenerIndex);
void ma_engine_listener_set_direction(ma_engine* pEngine, ma_uint32 listenerIndex, float x, float y, float z);
ma_vec3f ma_engine_listener_get_direction(const ma_engine* pEngine, ma_uint32 listenerIndex);
void ma_engine_listener_set_velocity(ma_engine* pEngine, ma_uint32 listenerIndex, float x, float y, float z);
ma_vec3f ma_engine_listener_get_velocity(const ma_engine* pEngine, ma_uint32 listenerIndex);
void ma_engine_listener_set_cone(ma_engine* pEngine, ma_uint32 listenerIndex, float innerAngleInRadians, float outerAngleInRadians, float outerGain);
void ma_engine_listener_get_cone(const ma_engine* pEngine, ma_uint32 listenerIndex, float* pInnerAngleInRadians, float* pOuterAngleInRadians, float* pOuterGain);
void ma_engine_listener_set_world_up(ma_engine* pEngine, ma_uint32 listenerIndex, float x, float y, float z);
ma_vec3f ma_engine_listener_get_world_up(const ma_engine* pEngine, ma_uint32 listenerIndex);
void ma_engine_listener_set_enabled(ma_engine* pEngine, ma_uint32 listenerIndex, ma_bool32 isEnabled);
ma_bool32 ma_engine_listener_is_enabled(const ma_engine* pEngine, ma_uint32 listenerIndex);
ma_result ma_engine_play_sound_ex(ma_engine* pEngine, const char* pFilePath, ma_node* pNode, ma_uint32 nodeInputBusIndex);
ma_result ma_engine_play_sound(ma_engine* pEngine, const char* pFilePath, ma_sound_group* pGroup);

ma_sound_config ma_sound_config_init(void);
ma_sound_config ma_sound_config_init_2(ma_engine* pEngine);
ma_result ma_sound_init_from_file(ma_engine* pEngine, const char* pFilePath, ma_uint32 flags, ma_sound_group* pGroup, ma_fence* pDoneFence, ma_sound* pSound);
ma_result ma_sound_init_from_file_w(ma_engine* pEngine, const wchar_t* pFilePath, ma_uint32 flags, ma_sound_group* pGroup, ma_fence* pDoneFence, ma_sound* pSound);
ma_result ma_sound_init_copy(ma_engine* pEngine, const ma_sound* pExistingSound, ma_uint32 flags, ma_sound_group* pGroup, ma_sound* pSound);
ma_result ma_sound_init_from_data_source(ma_engine* pEngine, ma_data_source* pDataSource, ma_uint32 flags, ma_sound_group* pGroup, ma_sound* pSound);
ma_result ma_sound_init_ex(ma_engine* pEngine, const ma_sound_config* pConfig, ma_sound* pSound);
void ma_sound_uninit(ma_sound* pSound);
ma_engine* ma_sound_get_engine(const ma_sound* pSound);
ma_data_source* ma_sound_get_data_source(const ma_sound* pSound);
ma_result ma_sound_start(ma_sound* pSound);
ma_result ma_sound_stop(ma_sound* pSound);
ma_result ma_sound_stop_with_fade_in_pcm_frames(ma_sound* pSound, ma_uint64 fadeLengthInFrames);
ma_result ma_sound_stop_with_fade_in_milliseconds(ma_sound* pSound, ma_uint64 fadeLengthInMilliseconds);
void ma_sound_set_volume(ma_sound* pSound, float volume);
float ma_sound_get_volume(const ma_sound* pSound);
void ma_sound_set_pan(ma_sound* pSound, float pan);
float ma_sound_get_pan(const ma_sound* pSound);
void ma_sound_set_pan_mode(ma_sound* pSound, ma_pan_mode panMode);
ma_pan_mode ma_sound_get_pan_mode(const ma_sound* pSound);
void ma_sound_set_pitch(ma_sound* pSound, float pitch);
float ma_sound_get_pitch(const ma_sound* pSound);
void ma_sound_set_spatialization_enabled(ma_sound* pSound, ma_bool32 enabled);
ma_bool32 ma_sound_is_spatialization_enabled(const ma_sound* pSound);
void ma_sound_set_pinned_listener_index(ma_sound* pSound, ma_uint32 listenerIndex);
ma_uint32 ma_sound_get_pinned_listener_index(const ma_sound* pSound);
ma_uint32 ma_sound_get_listener_index(const ma_sound* pSound);
ma_vec3f ma_sound_get_direction_to_listener(const ma_sound* pSound);
void ma_sound_set_position(ma_sound* pSound, float x, float y, float z);
ma_vec3f ma_sound_get_position(const ma_sound* pSound);
void ma_sound_set_direction(ma_sound* pSound, float x, float y, float z);
ma_vec3f ma_sound_get_direction(const ma_sound* pSound);
void ma_sound_set_velocity(ma_sound* pSound, float x, float y, float z);
ma_vec3f ma_sound_get_velocity(const ma_sound* pSound);
void ma_sound_set_attenuation_model(ma_sound* pSound, ma_attenuation_model attenuationModel);
ma_attenuation_model ma_sound_get_attenuation_model(const ma_sound* pSound);
void ma_sound_set_positioning(ma_sound* pSound, ma_positioning positioning);
ma_positioning ma_sound_get_positioning(const ma_sound* pSound);
void ma_sound_set_rolloff(ma_sound* pSound, float rolloff);
float ma_sound_get_rolloff(const ma_sound* pSound);
void ma_sound_set_min_gain(ma_sound* pSound, float minGain);
float ma_sound_get_min_gain(const ma_sound* pSound);
void ma_sound_set_max_gain(ma_sound* pSound, float maxGain);
float ma_sound_get_max_gain(const ma_sound* pSound);
void ma_sound_set_min_distance(ma_sound* pSound, float minDistance);
float ma_sound_get_min_distance(const ma_sound* pSound);
void ma_sound_set_max_distance(ma_sound* pSound, float maxDistance);
float ma_sound_get_max_distance(const ma_sound* pSound);
void ma_sound_set_cone(ma_sound* pSound, float innerAngleInRadians, float outerAngleInRadians, float outerGain);
void ma_sound_get_cone(const ma_sound* pSound, float* pInnerAngleInRadians, float* pOuterAngleInRadians, float* pOuterGain);
void ma_sound_set_doppler_factor(ma_sound* pSound, float dopplerFactor);
float ma_sound_get_doppler_factor(const ma_sound* pSound);
void ma_sound_set_directional_attenuation_factor(ma_sound* pSound, float directionalAttenuationFactor);
float ma_sound_get_directional_attenuation_factor(const ma_sound* pSound);
void ma_sound_set_fade_in_pcm_frames(ma_sound* pSound, float volumeBeg, float volumeEnd, ma_uint64 fadeLengthInFrames);
void ma_sound_set_fade_in_milliseconds(ma_sound* pSound, float volumeBeg, float volumeEnd, ma_uint64 fadeLengthInMilliseconds);
void ma_sound_set_fade_start_in_pcm_frames(ma_sound* pSound, float volumeBeg, float volumeEnd, ma_uint64 fadeLengthInFrames, ma_uint64 absoluteGlobalTimeInFrames);
void ma_sound_set_fade_start_in_milliseconds(ma_sound* pSound, float volumeBeg, float volumeEnd, ma_uint64 fadeLengthInMilliseconds, ma_uint64 absoluteGlobalTimeInMilliseconds);
float ma_sound_get_current_fade_volume(const ma_sound* pSound);
void ma_sound_set_start_time_in_pcm_frames(ma_sound* pSound, ma_uint64 absoluteGlobalTimeInFrames);
void ma_sound_set_start_time_in_milliseconds(ma_sound* pSound, ma_uint64 absoluteGlobalTimeInMilliseconds);
void ma_sound_set_stop_time_in_pcm_frames(ma_sound* pSound, ma_uint64 absoluteGlobalTimeInFrames);
void ma_sound_set_stop_time_in_milliseconds(ma_sound* pSound, ma_uint64 absoluteGlobalTimeInMilliseconds);
void ma_sound_set_stop_time_with_fade_in_pcm_frames(ma_sound* pSound, ma_uint64 stopAbsoluteGlobalTimeInFrames, ma_uint64 fadeLengthInFrames);
void ma_sound_set_stop_time_with_fade_in_milliseconds(ma_sound* pSound, ma_uint64 stopAbsoluteGlobalTimeInMilliseconds, ma_uint64 fadeLengthInMilliseconds);
ma_bool32 ma_sound_is_playing(const ma_sound* pSound);
ma_uint64 ma_sound_get_time_in_pcm_frames(const ma_sound* pSound);
ma_uint64 ma_sound_get_time_in_milliseconds(const ma_sound* pSound);
void ma_sound_set_looping(ma_sound* pSound, ma_bool32 isLooping);
ma_bool32 ma_sound_is_looping(const ma_sound* pSound);
ma_bool32 ma_sound_at_end(const ma_sound* pSound);
ma_result ma_sound_seek_to_pcm_frame(ma_sound* pSound, ma_uint64 frameIndex);
ma_result ma_sound_seek_to_second(ma_sound* pSound, float seekPointInSeconds);
ma_result ma_sound_get_data_format(ma_sound* pSound, ma_format* pFormat, ma_uint32* pChannels, ma_uint32* pSampleRate, ma_channel* pChannelMap, size_t channelMapCap);
ma_result ma_sound_get_cursor_in_pcm_frames(ma_sound* pSound, ma_uint64* pCursor);
ma_result ma_sound_get_length_in_pcm_frames(ma_sound* pSound, ma_uint64* pLength);
ma_result ma_sound_get_cursor_in_seconds(ma_sound* pSound, float* pCursor);
ma_result ma_sound_get_length_in_seconds(ma_sound* pSound, float* pLength);
ma_result ma_sound_set_end_callback(ma_sound* pSound, ma_sound_end_proc callback, void* pUserData);

ma_sound_group_config ma_sound_group_config_init(void);
ma_sound_group_config ma_sound_group_config_init_2(ma_engine* pEngine);
ma_result ma_sound_group_init(ma_engine* pEngine, ma_uint32 flags, ma_sound_group* pParentGroup, ma_sound_group* pGroup);
ma_result ma_sound_group_init_ex(ma_engine* pEngine, const ma_sound_group_config* pConfig, ma_sound_group* pGroup);
void ma_sound_group_uninit(ma_sound_group* pGroup);
ma_engine* ma_sound_group_get_engine(const ma_sound_group* pGroup);
ma_result ma_sound_group_start(ma_sound_group* pGroup);
ma_result ma_sound_group_stop(ma_sound_group* pGroup);
void ma_sound_group_set_volume(ma_sound_group* pGroup, float volume);
float ma_sound_group_get_volume(const ma_sound_group* pGroup);
void ma_sound_group_set_pan(ma_sound_group* pGroup, float pan);
float ma_sound_group_get_pan(const ma_sound_group* pGroup);
void ma_sound_group_set_pan_mode(ma_sound_group* pGroup, ma_pan_mode panMode);
ma_pan_mode ma_sound_group_get_pan_mode(const ma_sound_group* pGroup);
void ma_sound_group_set_pitch(ma_sound_group* pGroup, float pitch);
float ma_sound_group_get_pitch(const ma_sound_group* pGroup);
void ma_sound_group_set_spatialization_enabled(ma_sound_group* pGroup, ma_bool32 enabled);
ma_bool32 ma_sound_group_is_spatialization_enabled(const ma_sound_group* pGroup);
void ma_sound_group_set_pinned_listener_index(ma_sound_group* pGroup, ma_uint32 listenerIndex);
ma_uint32 ma_sound_group_get_pinned_listener_index(const ma_sound_group* pGroup);
ma_uint32 ma_sound_group_get_listener_index(const ma_sound_group* pGroup);
ma_vec3f ma_sound_group_get_direction_to_listener(const ma_sound_group* pGroup);
void ma_sound_group_set_position(ma_sound_group* pGroup, float x, float y, float z);
ma_vec3f ma_sound_group_get_position(const ma_sound_group* pGroup);
void ma_sound_group_set_direction(ma_sound_group* pGroup, float x, float y, float z);
ma_vec3f ma_sound_group_get_direction(const ma_sound_group* pGroup);
void ma_sound_group_set_velocity(ma_sound_group* pGroup, float x, float y, float z);
ma_vec3f ma_sound_group_get_velocity(const ma_sound_group* pGroup);
void ma_sound_group_set_attenuation_model(ma_sound_group* pGroup, ma_attenuation_model attenuationModel);
ma_attenuation_model ma_sound_group_get_attenuation_model(const ma_sound_group* pGroup);
void ma_sound_group_set_positioning(ma_sound_group* pGroup, ma_positioning positioning);
ma_positioning ma_sound_group_get_positioning(const ma_sound_group* pGroup);
void ma_sound_group_set_rolloff(ma_sound_group* pGroup, float rolloff);
float ma_sound_group_get_rolloff(const ma_sound_group* pGroup);
void ma_sound_group_set_min_gain(ma_sound_group* pGroup, float minGain);
float ma_sound_group_get_min_gain(const ma_sound_group* pGroup);
void ma_sound_group_set_max_gain(ma_sound_group* pGroup, float maxGain);
float ma_sound_group_get_max_gain(const ma_sound_group* pGroup);
void ma_sound_group_set_min_distance(ma_sound_group* pGroup, float minDistance);
float ma_sound_group_get_min_distance(const ma_sound_group* pGroup);
void ma_sound_group_set_max_distance(ma_sound_group* pGroup, float maxDistance);
float ma_sound_group_get_max_distance(const ma_sound_group* pGroup);
void ma_sound_group_set_cone(ma_sound_group* pGroup, float innerAngleInRadians, float outerAngleInRadians, float outerGain);
void ma_sound_group_get_cone(const ma_sound_group* pGroup, float* pInnerAngleInRadians, float* pOuterAngleInRadians, float* pOuterGain);
void ma_sound_group_set_doppler_factor(ma_sound_group* pGroup, float dopplerFactor);
float ma_sound_group_get_doppler_factor(const ma_sound_group* pGroup);
void ma_sound_group_set_directional_attenuation_factor(ma_sound_group* pGroup, float directionalAttenuationFactor);
float ma_sound_group_get_directional_attenuation_factor(const ma_sound_group* pGroup);
void ma_sound_group_set_fade_in_pcm_frames(ma_sound_group* pGroup, float volumeBeg, float volumeEnd, ma_uint64 fadeLengthInFrames);
void ma_sound_group_set_fade_in_milliseconds(ma_sound_group* pGroup, float volumeBeg, float volumeEnd, ma_uint64 fadeLengthInMilliseconds);
float ma_sound_group_get_current_fade_volume(ma_sound_group* pGroup);
void ma_sound_group_set_start_time_in_pcm_frames(ma_sound_group* pGroup, ma_uint64 absoluteGlobalTimeInFrames);
void ma_sound_group_set_start_time_in_milliseconds(ma_sound_group* pGroup, ma_uint64 absoluteGlobalTimeInMilliseconds);
void ma_sound_group_set_stop_time_in_pcm_frames(ma_sound_group* pGroup, ma_uint64 absoluteGlobalTimeInFrames);
void ma_sound_group_set_stop_time_in_milliseconds(ma_sound_group* pGroup, ma_uint64 absoluteGlobalTimeInMilliseconds);
ma_bool32 ma_sound_group_is_playing(const ma_sound_group* pGroup);
ma_uint64 ma_sound_group_get_time_in_pcm_frames(const ma_sound_group* pGroup);

ma_engine_node_config ma_engine_node_config_init(ma_engine* pEngine, ma_engine_node_type type, ma_uint32 flags);
ma_result ma_engine_node_get_heap_size(const ma_engine_node_config* pConfig, size_t* pHeapSizeInBytes);
ma_result ma_engine_node_init_preallocated(const ma_engine_node_config* pConfig, void* pHeap, ma_engine_node* pEngineNode);
ma_result ma_engine_node_init(const ma_engine_node_config* pConfig, const ma_allocation_callbacks* pAllocationCallbacks, ma_engine_node* pEngineNode);
void ma_engine_node_uninit(ma_engine_node* pEngineNode, const ma_allocation_callbacks* pAllocationCallbacks);
