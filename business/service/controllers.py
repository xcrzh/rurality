from django.db import transaction
from django.db.models import Q

from base import errors
from base import controllers as base_ctl
from business.service.models import ServiceModel
from business.service.models import ServiceUserModel
from utils.onlyone import onlyone


@onlyone.lock(ServiceModel.model_sign, 'name:sign', 'sign', 30)
@onlyone.lock(ServiceModel.model_sign, 'name', 'name', 30)
def create_service(name, sign, project_id, remark=None, operator=None):
    '''
    创建服务
    '''
    if ServiceModel.objects.filter(name=name).exists():
        raise errors.CommonError('服务名称已存在')
    if ServiceModel.objects.filter(sign=sign).exists():
        raise errors.CommonError('服务标识已存在')
    data = {
        'name': name,
        'sign': sign,
        'project_id': project_id,
        'remark': remark,
    }
    obj = base_ctl.create_obj(ServiceModel, data, operator)
    data = obj.to_dict()
    return data


@onlyone.lock(ServiceModel.model_sign, 'obj_id:name:sign', 'sign', 30)
@onlyone.lock(ServiceModel.model_sign, 'obj_id:name', 'name', 30)
@onlyone.lock(ServiceModel.model_sign, 'obj_id', 'obj_id', 30)
def update_service(obj_id, name, sign, project_id, remark=None, operator=None):
    '''
    编辑服务
    '''
    if ServiceModel.objects.filter(name=name).exclude(id=obj_id).exists():
        raise errors.CommonError('服务名称已存在')
    if ServiceModel.objects.filter(sign=sign).exclude(id=obj_id).exists():
        raise errors.CommonError('服务标识已存在')
    data = {
        'name': name,
        'sign': sign,
        'project_id': project_id,
        'remark': remark,
    }
    obj = base_ctl.update_obj(ServiceModel, obj_id, data, operator)
    data = obj.to_dict()
    return data


@onlyone.lock(ServiceModel.model_sign, 'obj_id', 'obj_id', 30)
def delete_service(obj_id, operator=None):
    '''
    删除服务
    '''
    base_ctl.delete_obj(ServiceModel, obj_id, operator)


def get_services(keyword=None, project_id=None, page_num=None, page_size=None, operator=None):
    '''
    获取服务列表
    '''
    base_query = ServiceModel.objects
    if keyword:
        base_query = base_query.filter(Q(name__icontains=keyword)|
                                       Q(sign__icontains=keyword))
    if project_id:
        base_query = base_query.filter(project_id=project_id)
    total = base_query.count()
    objs = base_ctl.query_objs_by_page(base_query, page_num, page_size)
    data_list = [obj.to_dict() for obj in objs]
    data = {
        'total': total,
        'data_list': data_list,
    }
    return data


def get_service(obj_id, operator=None):
    '''
    获取服务信息
    '''
    obj = base_ctl.get_obj(ServiceModel, obj_id)
    data = obj.to_dict()
    return data


@onlyone.lock(ServiceUserModel.model_sign, 'obj_id:user_id', 'obj_id:user_id', 30)
def create_service_user(obj_id, user_id, typ, operator=None):
    '''
    创建服务关联用户
    '''
    query = {
        'service_id': obj_id,
        'user_id': user_id,
    }
    if ServiceUserModel.objects.filter(**query).exists():
        raise errors.CommonError('用户已在此服务中')
    if not ServiceUserModel.check_choices('typ', typ):
        raise errors.CommonError('类型值不正确')
    data = {
        'service_id': obj_id,
        'user_id': user_id,
        'typ': typ,
    }
    obj = base_ctl.create_obj(ServiceUserModel, data, operator)
    data = obj.to_dict()
    return data


@onlyone.lock(ServiceUserModel.model_sign, 'obj_id:user_id', 'obj_id:user_id', 30)
def update_service_user(obj_id, user_id, typ, operator=None):
    '''
    编辑服务关联用户
    '''
    query = {
        'service_id': obj_id,
        'user_id': user_id,
    }
    obj = ServiceUserModel.objects.filter(**query).first()
    if not obj:
        raise errors.CommonError('用户未在此服务中')
    if not ServiceUserModel.check_choices('typ', typ):
        raise errors.CommonError('类型值不正确')
    data = {
        'typ': typ,
    }
    obj = base_ctl.update_obj(ServiceUserModel, obj.id, data, operator)
    data = obj.to_dict()
    return data


@onlyone.lock(ServiceUserModel.model_sign, 'obj_id:user_id', 'obj_id:user_id', 30)
def delete_service_user(obj_id, user_id, operator=None):
    '''
    删除服务关联用户
    '''
    query = {
        'service_id': obj_id,
        'user_id': user_id,
    }
    obj = ServiceUserModel.objects.filter(**query).first()
    if not obj:
        raise errors.CommonError('用户未在此项目中')
    base_ctl.delete_obj(ServiceUserModel, obj.id, operator)


def get_service_users(obj_id, typ=None, page_num=None, page_size=None, operator=None):
    '''
    获取服务用户列表
    '''
    base_query = ServiceUserModel.objects.filter(service_id=obj_id)\
            .filter(user__is_deleted=False).select_related('user')
    if typ:
        base_query = base_query.filter(typ=typ)
    total = base_query.count()
    objs = base_ctl.query_objs_by_page(base_query, page_num, page_size)
    data_list = []
    for obj in objs:
        data = obj.to_dict()
        data['user'] = obj.user.to_dict()
        data_list.append(data)
    data = {
        'total': total,
        'data_list': data_list,
    }
    return data
