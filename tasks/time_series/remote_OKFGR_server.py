import subprocess

OK_GREECE_ROOT = "http://okfnrg.math.auth.gr"
OKFGR_TimeSeries_EndPoint = "/ocpu/library/TimeSeries.OBeu/R/tsa.obeu"
OKFGR_DM_Github = "https://github.com/okgreece/TimeSeries.OBeu"


def dm_okfgr(endpoint, **kwargs):
    arglst = []
    for k in kwargs.keys():
        arglst += ["-d", str(k)+"="+str(kwargs[k])]
    cmd = ['curl'] + arglst + [OK_GREECE_ROOT+endpoint]
    res = subprocess.check_output(cmd).decode("utf-8")
    result_endpoint = res.split('\n')[0]
    result = subprocess.check_output(['curl', OK_GREECE_ROOT+result_endpoint+'/print']).decode("utf-8")
    return result


if __name__ == "__main__":
    jsonStr = dm_okfgr("/ocpu/library/OBeU/R/ts.obeu", tsdata="Athens_draft_ts", prediction_steps=4)
    print(jsonStr)

    jsonStr = dm_okfgr(OKFGR_TimeSeries_EndPoint, tsdata="Athens_draft_ts", h=4)
    print(jsonStr)