"""短信验证码 - 阿里云号码认证服务 (dypnsapi)"""
import time, os, json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

def verify_sms_code(phone: str, code: str) -> bool:
    """供其他模块调用的验证码校验（调阿里云 CheckSmsVerifyCode）"""
    try:
        result = _call_dypnsapi("CheckSmsVerifyCode", {
            "PhoneNumber": phone,
            "VerifyCode": code,
        })
        return result.get("Model", {}).get("VerifyResult") == "PASS"
    except Exception as e:
        print(f"[SMS] 核验失败: {e}")
        return False


router = APIRouter(prefix="/api/sms", tags=["短信"])

SMS_ACCESS_KEY = os.environ.get("SMS_ACCESS_KEY", "")
SMS_ACCESS_SECRET = os.environ.get("SMS_ACCESS_SECRET", "")
SMS_SIGN_NAME = os.environ.get("SMS_SIGN_NAME", "恒创联众")
SMS_TEMPLATE_CODE = os.environ.get("SMS_TEMPLATE_CODE", "100001")

# 防刷：记录手机号上次发送时间
_last_send = {}  # {phone: timestamp}


class SendReq(BaseModel):
    phone: str


class VerifyReq(BaseModel):
    phone: str
    code: str


@router.post("/send")
def send_sms(req: SendReq):
    """发送验证码（阿里云端自动生成验证码并下发短信）"""
    phone = req.phone.strip()
    if not phone or len(phone) != 11 or not phone.startswith("1"):
        raise HTTPException(400, "请输入正确的手机号")

    # 60秒内不重复发
    now = time.time()
    if phone in _last_send and now - _last_send[phone] < 60:
        wait = int(60 - (now - _last_send[phone]))
        raise HTTPException(429, f"请{wait}秒后再发送")

    out_id = f"{phone}_{int(now * 1000)}"
    _last_send[phone] = now

    try:
        _call_dypnsapi("SendSmsVerifyCode", {
            "PhoneNumber": phone,
            "SignName": SMS_SIGN_NAME,
            "TemplateCode": SMS_TEMPLATE_CODE,
            "TemplateParam": json.dumps({"code": "##code##", "min": "5"}),
            "OutId": out_id,
            "CodeLength": 6,
        })
        print(f"[SMS] 短信已发送到 {phone}")
    except Exception as e:
        print(f"[SMS] 发送失败: {e}")
        raise HTTPException(500, f"短信发送失败: {e}")

    return {"message": "验证码已发送", "out_id": out_id}


@router.post("/verify")
def verify_sms_endpoint(req: VerifyReq):
    """核验验证码"""
    if verify_sms_code(req.phone.strip(), req.code):
        return {"valid": True, "message": "验证通过"}
    return {"valid": False, "message": "验证码错误"}


def _call_dypnsapi(action: str, biz_params: dict) -> dict:
    """调用阿里云号码认证服务 API (dypnsapi.aliyuncs.com)"""
    import hmac, hashlib, base64, urllib.request, uuid
    from urllib.request import HTTPError
    from datetime import datetime, timezone

    params = {
        "AccessKeyId": SMS_ACCESS_KEY,
        "Action": action,
        "Format": "JSON",
        "SignatureMethod": "HMAC-SHA1",
        "SignatureNonce": str(uuid.uuid4()),
        "SignatureVersion": "1.0",
        "Timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "Version": "2017-05-25",
    }
    params.update(biz_params)

    query = "&".join(f"{k}={_url_encode(str(params[k]))}" for k in sorted(params.keys()))
    sign_str = f"GET&{_url_encode('/')}&{_url_encode(query)}"
    signature = base64.b64encode(
        hmac.new(f"{SMS_ACCESS_SECRET}&".encode(), sign_str.encode(), hashlib.sha1).digest()
    ).decode()

    url = f"https://dypnsapi.aliyuncs.com/?Signature={_url_encode(signature)}&{query}"

    proxy_handler = urllib.request.ProxyHandler({})
    opener = urllib.request.build_opener(proxy_handler, urllib.request.HTTPSHandler())
    try:
        resp = opener.open(url)
        body = json.loads(resp.read().decode())
    except HTTPError as e:
        err_body = e.read().decode()
        raise Exception(f"HTTP {e.code}: {err_body}")
    if body.get("Code") != "OK":
        raise Exception(f"{body.get('Code')}: {body.get('Message')}")
    return body


def _url_encode(s: str) -> str:
    import urllib.parse
    return urllib.parse.quote(s, safe="")
