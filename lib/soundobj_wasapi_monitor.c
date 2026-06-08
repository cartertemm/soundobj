/*
 * soundobj_wasapi_monitor.c
 *
 * A secondary IMMNotificationClient registered alongside miniaudio's own to
 * handle PKEY_AudioEngine_DeviceFormat property changes - i.e. the user
 * changed the sample rate or bit depth in Windows Sound settings. Miniaudio's
 * built-in handler ignores this notification.
* We perform the same task (reroute and reinit) so playback resumes without the need to restart the app.
 *
 * This file must be #include-d after MINIAUDIO_IMPLEMENTATION in the same
 * translation unit so the otherwise-static internals (ma_device_reroute__wasapi,
 * ma_device_get_state, etc.) are in scope.
 */

#if defined(MA_WIN32_DESKTOP) || defined(MA_WIN32_GDK)

typedef struct {
	void*      lpVtbl;   /* must be first - COM vtable pointer */
	ma_uint32  counter;  /* ref count - mirrors ma_IMMNotificationClient layout */
	ma_engine* pEngine;
} soundobj_nc;


static HRESULT STDMETHODCALLTYPE soundobj_nc_QueryInterface(
	ma_IMMNotificationClient* pSelf, const IID* const riid, void** ppObject)
{
	if (ma_is_guid_equal(riid, &MA_IID_IUnknown) ||
	    ma_is_guid_equal(riid, &MA_IID_IMMNotificationClient))
	{
		*ppObject = pSelf;
		ma_atomic_fetch_add_32(&((soundobj_nc*)pSelf)->counter, 1);
		return S_OK;
	}
	*ppObject = NULL;
	return E_NOINTERFACE;
}

static ULONG STDMETHODCALLTYPE soundobj_nc_AddRef(ma_IMMNotificationClient* pSelf)
{
	return (ULONG)ma_atomic_fetch_add_32(&((soundobj_nc*)pSelf)->counter, 1) + 1;
}

static ULONG STDMETHODCALLTYPE soundobj_nc_Release(ma_IMMNotificationClient* pSelf)
{
	return (ULONG)ma_atomic_fetch_sub_32(&((soundobj_nc*)pSelf)->counter, 1) - 1;
}

static HRESULT STDMETHODCALLTYPE soundobj_nc_OnDeviceStateChanged(
	ma_IMMNotificationClient* pSelf, const WCHAR* pDeviceID, DWORD dwNewState)
{ (void)pSelf; (void)pDeviceID; (void)dwNewState; return S_OK; }

static HRESULT STDMETHODCALLTYPE soundobj_nc_OnDeviceAdded(
	ma_IMMNotificationClient* pSelf, const WCHAR* pDeviceID)
{ (void)pSelf; (void)pDeviceID; return S_OK; }

static HRESULT STDMETHODCALLTYPE soundobj_nc_OnDeviceRemoved(
	ma_IMMNotificationClient* pSelf, const WCHAR* pDeviceID)
{ (void)pSelf; (void)pDeviceID; return S_OK; }

static HRESULT STDMETHODCALLTYPE soundobj_nc_OnDefaultDeviceChanged(
	ma_IMMNotificationClient* pSelf, ma_EDataFlow dataFlow, ma_ERole role,
	const WCHAR* pDefaultDeviceID)
{ (void)pSelf; (void)dataFlow; (void)role; (void)pDefaultDeviceID; return S_OK; }

static HRESULT STDMETHODCALLTYPE soundobj_nc_OnPropertyValueChanged(
	ma_IMMNotificationClient* pSelf, const WCHAR* pDeviceID, const PROPERTYKEY key)
{
	soundobj_nc* pThis = (soundobj_nc*)pSelf;
	ma_device* pDevice;
	ma_bool32 wasStarted;
	ma_bool8 isPlayback, isCapture, isLoopback, rerouted;
	if (pDeviceID == NULL || pThis->pEngine == NULL)
		return S_OK;
	/* We only really care about format (sample rate / bit depth) changes */
	if (!ma_is_guid_equal(&key.fmtid, &MA_PKEY_AudioEngine_DeviceFormat.fmtid) ||
	    key.pid != MA_PKEY_AudioEngine_DeviceFormat.pid)
		return S_OK;
	pDevice = ma_engine_get_device(pThis->pEngine);
	if (pDevice == NULL)
		return S_OK;
	wasStarted = (ma_device_get_state(pDevice) == ma_device_state_started);
	isPlayback = (pDevice->type == ma_device_type_playback || pDevice->type == ma_device_type_duplex);
	isCapture  = (pDevice->type == ma_device_type_capture  || pDevice->type == ma_device_type_duplex);
	isLoopback = (pDevice->type == ma_device_type_loopback);
	rerouted   = MA_FALSE;
	ma_mutex_lock(&pDevice->wasapi.rerouteLock);
	if (isPlayback && wcscmp(pDeviceID, (const WCHAR*)pDevice->playback.id.wasapi) == 0) {
		if (ma_device_reroute__wasapi(pDevice, ma_device_type_playback) == MA_SUCCESS)
			rerouted = MA_TRUE;
	}
	if ((isCapture || isLoopback) && wcscmp(pDeviceID, (const WCHAR*)pDevice->capture.id.wasapi) == 0) {
		ma_device_type captureType = isLoopback ? ma_device_type_loopback : ma_device_type_capture;
		if (ma_device_reroute__wasapi(pDevice, captureType) == MA_SUCCESS)
			rerouted = MA_TRUE;
	}
	ma_mutex_unlock(&pDevice->wasapi.rerouteLock);
	if (rerouted && wasStarted)
		ma_device_start(pDevice);
	return S_OK;
}

static ma_IMMNotificationClientVtbl g_soundobj_nc_vtbl = {
	soundobj_nc_QueryInterface,
	soundobj_nc_AddRef,
	soundobj_nc_Release,
	soundobj_nc_OnDeviceStateChanged,
	soundobj_nc_OnDeviceAdded,
	soundobj_nc_OnDeviceRemoved,
	soundobj_nc_OnDefaultDeviceChanged,
	soundobj_nc_OnPropertyValueChanged
};

static soundobj_nc  g_soundobj_nc_inst;
static ma_bool8     g_soundobj_nc_registered = MA_FALSE;


void soundobj_wasapi_monitor_init(ma_engine* pEngine)
{
	ma_device* pDevice;
	ma_IMMDeviceEnumerator* pEnum;
	HRESULT hr;
	if (pEngine == NULL) return;
	pDevice = ma_engine_get_device(pEngine);
	if (pDevice == NULL) return;
	/* pDeviceEnumerator is NULL if WASAPI notification registration failed at device init */
	pEnum = (ma_IMMDeviceEnumerator*)pDevice->wasapi.pDeviceEnumerator;
	if (pEnum == NULL) return;
	g_soundobj_nc_inst.lpVtbl  = (void*)&g_soundobj_nc_vtbl;
	g_soundobj_nc_inst.counter = 1;
	g_soundobj_nc_inst.pEngine = pEngine;
	hr = ma_IMMDeviceEnumerator_RegisterEndpointNotificationCallback(
		pEnum, (ma_IMMNotificationClient*)&g_soundobj_nc_inst);
	g_soundobj_nc_registered = SUCCEEDED(hr) ? MA_TRUE : MA_FALSE;
}

void soundobj_wasapi_monitor_uninit(ma_engine* pEngine)
{
	ma_device* pDevice;
	ma_IMMDeviceEnumerator* pEnum;
	if (!g_soundobj_nc_registered || pEngine == NULL) return;
	pDevice = ma_engine_get_device(pEngine);
	if (pDevice == NULL) return;
	pEnum = (ma_IMMDeviceEnumerator*)pDevice->wasapi.pDeviceEnumerator;
	if (pEnum != NULL) {
		ma_IMMDeviceEnumerator_UnregisterEndpointNotificationCallback(
			pEnum, (ma_IMMNotificationClient*)&g_soundobj_nc_inst);
	}
	g_soundobj_nc_inst.pEngine = NULL;
	g_soundobj_nc_registered = MA_FALSE;
}

#else /* Non-Windows: no-ops */

void soundobj_wasapi_monitor_init(ma_engine* pEngine) { (void)pEngine; }
void soundobj_wasapi_monitor_uninit(ma_engine* pEngine) { (void)pEngine; }

#endif
