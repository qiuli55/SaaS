import urllib.request, json

BASE = 'http://localhost:8000/api'
ok = 0; fail = 0

def req(method, path, data=None, token=None):
    url = BASE + path
    headers = {'Content-Type': 'application/json'}
    if token: headers['Authorization'] = f'Bearer {token}'
    body = data.encode() if data else None
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    return urllib.request.urlopen(r)

def test(name, func):
    global ok, fail
    try:
        result = func()
        ok += 1
        detail = ''
        if hasattr(result, 'read'):
            body = result.read().decode()[:100]
            detail = ' — ' + body.replace('\n',' ')
        print(f'  [OK] {name}{detail}')
    except Exception as e:
        fail += 1
        body = ''
        if hasattr(e, 'read'): 
            try: body = e.read().decode()[:200]
            except: pass
        print(f'  [FAIL] {name} — {e} {body}')

# 健康检查
test('健康检查', lambda: req('GET', '/health'))

# 注册
token = None
def do_register():
    global token
    resp = req('POST', '/user/register', json.dumps({'phone':'13900001111','password':'test123'}))
    token = json.loads(resp.read().decode())['access_token']
    return resp
test('用户注册', do_register)

# 登录
def do_login():
    global token
    resp = req('POST', '/user/login', json.dumps({'phone':'13900001111','password':'test123'}))
    token = json.loads(resp.read().decode())['access_token']
    return resp
test('用户登录', do_login)

# 创建案件
case_id = None
def do_create():
    global case_id
    resp = req('POST', '/cases', json.dumps({
        'case_type': '民间借贷纠纷', 'plaintiff': '王建国', 'defendant': '李伟强',
        'subject_amount': 150000,
        'description': '2024年3月李伟强向王建国借款15万元，约定年利率10%。到期后经多次催告仍未还款。',
        'plaintiff_detail': json.dumps({'gender':'男','birth':'1982年5月','address':'南京市鼓楼区中山路99号'}),
        'defendant_detail': json.dumps({'address':'南京市秦淮区建康路55号'}),
        'court_name': '南京市秦淮区人民法院'
    }), token=token)
    case_id = json.loads(resp.read().decode())['id']
    return resp
test('创建案件', do_create)

# 案件列表
test('案件列表', lambda: req('GET', '/cases', token=token))

# 案件详情
test('案件详情', lambda: req('GET', f'/cases/{case_id}', token=token))

# 更新案件
test('更新案件', lambda: req('PUT', f'/cases/{case_id}', json.dumps({'status':'待立案'}), token=token))

# AI生成文书
doc_id = None
def do_generate():
    global doc_id
    resp = req('POST', '/documents/generate', json.dumps({
        'case_id': case_id, 'doc_type': '民事起诉状',
        'claims': '1. 判令被告偿还借款本金15万元\n2. 判令被告支付利息1.5万元\n3. 诉讼费由被告承担',
        'facts': '2024年3月15日被告向原告借款15万元，约定年利率10%，一年后还本付息。到期后被告以经营困难为由拒不还款。',
        'plaintiff_info': json.dumps({'gender':'男','birth':'1982年5月','address':'南京市鼓楼区中山路99号'}),
        'defendant_info': json.dumps({'address':'南京市秦淮区建康路55号'}),
        'court_name': '南京市秦淮区人民法院'
    }), token=token)
    doc_id = json.loads(resp.read().decode())['data']['id']
    return resp
test('AI生成文书', do_generate)

# 文书详情
test('文书详情', lambda: req('GET', f'/documents/{doc_id}', token=token))

# 版本列表
test('文书版本', lambda: req('GET', f'/documents/{doc_id}/versions', token=token))

# 下载
test('下载Word', lambda: req('GET', f'/documents/{doc_id}/download/docx', token=token))
test('下载PDF', lambda: req('GET', f'/documents/{doc_id}/download/pdf', token=token))

# 历史
test('历史记录', lambda: req('GET', '/documents/history', token=token))

# 客户
client_id = None
def do_client():
    global client_id
    resp = req('POST', '/clients', json.dumps({'name':'王建国','phone':'13912345678','company':'南京建工集团','tags':json.dumps(['VIP客户'])}), token=token)
    client_id = json.loads(resp.read().decode())['data']['id']
    return resp
test('创建客户', do_client)
test('客户列表', lambda: req('GET', '/clients', token=token))

# 日程
schedule_id = None
def do_schedule():
    global schedule_id
    resp = req('POST', '/schedules', json.dumps({'event_type':'开庭','event_date':'2026-08-15T09:00:00','location':'秦淮区法院第2法庭','notes':'一审开庭'}), token=token)
    schedule_id = json.loads(resp.read().decode())['data']['id']
    return resp
test('创建日程', do_schedule)
test('日程列表', lambda: req('GET', '/schedules?month=2026-08', token=token))
test('标记完成', lambda: req('PUT', f'/schedules/{schedule_id}', json.dumps({'is_done':True}), token=token))

# 删除
test('删除日程', lambda: req('DELETE', f'/schedules/{schedule_id}', token=token))
test('删除案件', lambda: req('DELETE', f'/cases/{case_id}', token=token))
test('删除客户', lambda: req('DELETE', f'/clients/{client_id}', token=token))

# 前端可达性
import urllib.request as ur
try:
    resp = ur.urlopen('http://localhost:5173')
    print(f'  [OK] 前端页面 (HTTP {resp.status})')
    ok += 1
except Exception as e:
    print(f'  [FAIL] 前端页面 — {e}')
    fail += 1

print(f'\n===== 测试结果 =====')
print(f'通过: {ok}')
print(f'失败: {fail}')
print(f'总计: {ok+fail}')
print(f'通过率: {ok/(ok+fail)*100:.0f}%')
