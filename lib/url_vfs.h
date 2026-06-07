#pragma once
#include "miniaudio.h"

typedef struct {
	ma_vfs_callbacks cb;
	ma_default_vfs default_vfs;
} soundobj_url_vfs;

ma_vfs* soundobj_url_vfs_create(void);
void soundobj_url_vfs_destroy(ma_vfs* vfs);
