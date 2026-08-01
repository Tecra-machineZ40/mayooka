from django import forms
from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html, format_html_join
from django_ckeditor_5.widgets import CKEditor5Widget
from mptt.admin import MPTTModelAdmin

from . import models


class PostAdminForm(forms.ModelForm):
    class Meta:
        model = models.Post
        fields = "__all__"
        widgets = {
            "content": CKEditor5Widget(config_name="extends"),
            "seo_description": forms.Textarea(attrs={"rows": 3}),
        }


@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    list_display = ("title", "status", "category", "author", "publish", "views", "seo_ready")
    list_filter = ("status", "category", "publish", "author")
    search_fields = ("title", "excerpt", "content", "slug")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "publish"
    ordering = ("-publish",)
    filter_horizontal = ("saved_by",)
    list_per_page = 25
    readonly_fields = ("views", "image_preview", "seo_checklist")
    actions = ("make_published", "make_draft")

    fieldsets = (
        ("Contenu", {
            "fields": ("title", "slug", "category", "author", "status", "publish"),
        }),
        ("Texte", {
            "fields": ("excerpt", "content"),
        }),
        ("Media", {
            "fields": ("image_preview", "image", "image_alt"),
        }),
        ("SEO", {
            "fields": ("seo_title", "seo_description", "canonical_url", "seo_checklist"),
        }),
        ("Engagement", {
            "fields": ("views", "saved_by"),
        }),
    )

    def image_preview(self, obj):
        if not obj or not obj.image:
            return "Aucune image"
        return format_html(
            '<img src="{}" alt="{}" style="max-width: 280px; height: auto; border: 1px solid #cbd5e1;" />',
            obj.image.url,
            obj.image_alt or obj.title,
        )

    image_preview.short_description = "Aperçu image"

    def seo_checklist(self, obj):
        checks = [
            (bool(obj.seo_title) and 45 <= len(obj.seo_title) <= 65, "SEO title entre 45 et 65 caractères"),
            (bool(obj.seo_description) and 120 <= len(obj.seo_description) <= 160, "Meta description entre 120 et 160 caractères"),
            (bool(obj.image_alt), "Texte alternatif image renseigné"),
            (bool(obj.slug), "Slug présent"),
            (bool(obj.excerpt) and len(obj.excerpt) >= 90, "Extrait descriptif renseigné"),
            (bool(obj.canonical_url), "URL canonique définie"),
        ]
        items = [
            ("#047857" if is_valid else "#b91c1c", "✓" if is_valid else "✗", label)
            for is_valid, label in checks
        ]
        return format_html(
            '<ul style="margin:0; padding-left: 18px;">{}</ul>',
            format_html_join('', '<li style="color:{}">{} {}</li>', items),
        )

    seo_checklist.short_description = "Checklist SEO"

    def seo_ready(self, obj):
        checks = [
            bool(obj.seo_title) and 45 <= len(obj.seo_title) <= 65,
            bool(obj.seo_description) and 120 <= len(obj.seo_description) <= 160,
            bool(obj.image_alt),
            bool(obj.slug),
        ]
        ready = all(checks)
        color = "#047857" if ready else "#b91c1c"
        label = "OK" if ready else "A compléter"
        return format_html('<strong style="color:{}">{}</strong>', color, label)

    seo_ready.short_description = "SEO"

    @admin.action(description="Publier les articles sélectionnés")
    def make_published(self, request, queryset):
        updated = queryset.update(status="published", publish=timezone.now().date())
        self.message_user(request, f"{updated} article(s) publié(s).")

    @admin.action(description="Remettre en brouillon")
    def make_draft(self, request, queryset):
        updated = queryset.update(status="draft")
        self.message_user(request, f"{updated} article(s) remis en brouillon.")


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(models.Comment)
class CommentAdmin(MPTTModelAdmin):
    list_display = ("post", "name", "email", "publish", "status")
    list_filter = ("status", "publish")
    search_fields = ("name", "email", "content", "post__title")
