from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.admin.models import LogEntry

from .models import *
from .adminforms import PostAdminForm
from typeidea.custom_site import custom_site
from typeidea.base_admin import BaseOwnerAdmin
# Register your models here.


class PostInline(admin.TabularInline):

    fields = ('title', 'desc')
    extra = 1   # 控制额外多个
    model = Post

@admin.register(Category, site=custom_site)
class CategoryAdmin(BaseOwnerAdmin):
    inlines = [PostInline, ]
    list_display = ('name', 'status', 'is_nav', 'created_time', 'post_count')
    fields = ('name', 'status', 'is_nav')

    def post_count(self, obj):
        return obj.post_set.count()

    post_count.short_description = '文章数量'


@admin.register(Tag, site=custom_site)
class TagAdmin(BaseOwnerAdmin):
    list_display = ('name', 'status', 'created_time')
    fields = ('name', 'status')


class CategoryOwnFilter(admin.SimpleListFilter):
    """　自定义过滤器只显示当前用户分类 """
    title = '分类过滤器'
    parameter_name = 'own_category'

    def lookups(self, request, model_admin):
        return Category.objects.filter(owner=request.user).values_list('id', 'name')

    def queryset(self, request, queryset):
        category_id = self.value()

        if category_id:
            return queryset.filter(category_id=self.value())
        return queryset

@admin.register(Post, site=custom_site)
class PostAdmin(BaseOwnerAdmin):
    form = PostAdminForm
    list_display = [
        'title','desc',  'category', 'status',
        'created_time', 'operator',
        'owner'
    ]
    list_display_links = []

    list_filter = [CategoryOwnFilter]
    search_fields = ['title', 'category__name']

    actions_on_top = True
    actions_on_bottom = False


    # 编辑页面
    save_on_top = True

    exclude = ('owner',)
    """
    fields = (
        ('category', 'title'),
        'desc',
        'status',
        'content',
        'tag',
    )"""
    fieldsets = (
        ('基础配置', {
            'description': '基础配置描述',
            'fields': (
                ('title', 'category'),
                'status',
            ),
        }),
        ('内容', {
            'fields': (
                'desc',
                'content',
            )
        }),
        ('额外信息', {
            'classes': ('collapse', ),
            'fields': ('tag', )
        })
    )
    filter_vertical = ('tag', )

    def operator(self, obj):
        return format_html(
            '<a href="{}">编辑</a>',
            reverse('cus_admin:blog_post_change', args=(obj.id, ))
        )
    operator.short_description = '操作'

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(PostAdmin, self).save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super(PostAdmin, self).get_queryset(request)
        return qs.filter(owner=request.user)

    # 自定义静态文件引入
    # class Media:
    #     css = {
    #         'all': ("https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css", ),
    #     }
    #     js = ('https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js', )


@admin.register(LogEntry, site=custom_site)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('object_repr', 'object_id', 'action_flag', 'user',
                    'change_message')
admin.ModelAdmin.log_addition()