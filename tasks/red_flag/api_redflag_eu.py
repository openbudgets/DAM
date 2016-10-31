import subprocess
import json
from pprint import pprint

redflagHuWeb = "http://api-docs.redflags.eu/"
sampleOrgId = "ORG-7d022d90afad016a3dbbafd59800b1b6"
access_tdong = "&access_token=ab6ee183-64c1-4d60-b56e-e43cfd358476"
redflag_root = "http://api.redflags.eu"


def valid_orgId(orgId):
    if "ORG-" in orgId and len(orgId) == 36:
        return True
    else:
        return False


def get_organization_data(orgId):
    if valid_orgId(orgId):
        orgIdStr = "/organization?id={}".format(orgId)
        qstr = redflag_root + orgIdStr + access_tdong
        cmd = "curl '{}'".format(qstr)
        output = subprocess.check_output(cmd, shell=True).decode('utf8')
        dic = json.loads(output)
        return dic
    else:
        print("invalid organization id")
        return -1


def retrieve_org_id(nameLike='B'):
    dic = get_organizations(nameLike=nameLike)
    result = []
    for record in dic.get('result', []):
        result.append(record.get('id', ''))
    return list(filter(lambda ele: ele != '', result))


def retrieve_link_from_org_id(orgId, need_print=False):
    links = []
    orgData = get_organization_data(orgId)
    if need_print:
        pprint(orgData)
    result = orgData.get('result', {})
    calls = result.get('calls', [])
    for record in calls:
        links.append(record.get('url', ''))
    if need_print:
        pprint(links)
    return list(filter(lambda ele:ele != '', links))


def retrieve_link_by_name_pattern(nameLike = 'B'):
    links = []
    for orgId in retrieve_org_id(nameLike=nameLike):
        links0 = retrieve_link_from_org_id(orgId)
        pprint(links0)
        print(orgId, len(links0))
        links += links0
    return links


def get_organizations(count=50, page=1, nameLike='B'):
    org_data = "/organizations?count={}&page={}&nameLike={}".format(count, page, nameLike)
    qstr = redflag_root + org_data + access_tdong
    cmd = "curl '{}'".format(qstr)
    output = subprocess.check_output(cmd, shell=True).decode('utf8')
    dic = json.loads(output)
    return dic


if __name__ == "__main__":
    links = retrieve_link_by_name_pattern(nameLike='E')
    print(len(links))
    #retrieve_link_from_org_id("ORG-886f69c55ec58a53218a09df07ad0a70", need_print=True)
