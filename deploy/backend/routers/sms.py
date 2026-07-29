"""短信验证码 - 阿里云 SMS"""
import random, time, os, json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
from models import User

router = APIRouter(prefix="/api/sms", tags=["短信"])

SMS_ACCESS_KEY = os.environ.get("SMS_ACCESS_KEY", "")
SMS_ACCESS_SECRET = os.environ.get("SMS_ACCESS_SECRET", "")
SMS_SIGN_NAME = os.environ.get("SMS_SIGN_NAME", "")
SMS_TEMPLATE_CODE = os.environ.get("SMS_TEMPLATE_CODE", "")

# 内存存储验证码（重启清空，够用了）
codes = {}  # {phone: (code, expires_at)}


class SendReq(BaseModel):
    phone: str


class VerifyReq(BaseModel):
    phone: str
    code: str


@router.post("/send")
def send_sms(req: SendReq):
    """发送验证码"""
    phone = req.phone.strip()
    if not phone or len(phone) != 11 or not phone.startswith("1"):
        raise HTTPException(400, "请输入正确的手机号")

    # 60秒内不重复发
    if phone in codes:
        _, expires = codes[phone]
        if time.time() < expires - 240:  # 4分钟内已发过
            return {"message": "验证码已发送，请检查短信"}

    code = str(random.randint(100000, 999999))
    codes[phone] = (code, time.time() + 300)  # 5分钟有效

    if SMS_ACCESS_KEY and SMS_ACCESS_SECRET:
        try:
            _send_aliyun(phone, code)
        except Exception as e:
            print(f"[SMS] 发送失败: {e}")
            # 降级：开发/测试环境输出到控制台
            print(f"[SMS] {phone} 验证码: {code}")

    print(f"[SMS] {phone} 验证码: {code}")
    return {"message": "验证码已发送"}


@router.post("/verify")
def verify_sms(req: VerifyReq):
    """校验验证码"""
    if req.phone not in codes:
        return {"valid": False, "message": "请先发送验证码"}
    saved_code, expires = codes[req.phone]
    if time.time() > expires:
        del codes[req.phone]
        return {"valid": False, "message": "验证码已过期"}
    if saved_code != req.code:
        return {"valid": False, "message": "验证码错误"}
    return {"valid": True, "message": "验证通过"}


def _send_aliyun(phone: str, code: str):
    """阿里云 SendSms API"""
    import hmac, hashlib, base64, urllib.request, datetime

    params = {
        "AccessKeyId": SMS_ACCESS_KEY,
        "SignatureMethod": "HMAC-SHA1",
        "SignatureVersion": "1.0",
        "SignatureNonce": str(random.randint(100000000000, 999999999999)),
        "Timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "Format": "JSON",
        "Action": "SendSms",
        "Version": "2017-05-25",
        "RegionId": "cn-hangzhou",
        "PhoneNumbers": phone,
        "SignName": SMS_SIGN_NAME,
        "TemplateCode": SMS_TEMPLATE_CODE,
        "TemplateParam": json.dumps({"code": code}),
    }

    sorted_keys = sorted(params.keys())
    canonical = "&".join(
        f"{k}={_url_encode(str(params[k]))}" for k in sorted_keys
    )
    string_to_sign = f"GET&{_url_encode('/')}&{_url_encode(canonical)}"
    key = bytes(SMS_ACCESS_SECRET + "&", "utf-8")
    signature = base64.b64encode(
        hmac.new(key, string_to_sign.encode("utf-8"), hashlib.sha1).digest()
    ).decode()

    url = f"https://dysmsapi.aliyuncs.com/?Signature={_url_encode(signature)}&{canonical}"
    req = urllib.request.Request(url)
    resp = urllib.request.urlopen(req, timeout=10)
    result = json.loads(resp.read())
    if result.get("Code") != "OK":
        raise Exception(result.get("Message", "SendSms failed"))


def _url_encode(s: str) -> str:
    import urllib.parse
    return urllib.parse.quote(s, safe="")
