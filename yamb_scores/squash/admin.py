from django.contrib import admin

from .models import SquashMatch, SquashPlayer, SquashSession, SquashSet


class SquashSetInline(admin.TabularInline):
	model = SquashSet
	extra = 0


@admin.register(SquashMatch)
class SquashMatchAdmin(admin.ModelAdmin):
	list_display = ("id", "date_played", "player_1", "player_2", "created_at", "updated_at")
	list_filter = ("session", "date_played", "player_1", "player_2")
	search_fields = ("player_1__name", "player_2__name")
	date_hierarchy = "date_played"
	inlines = [SquashSetInline]


@admin.register(SquashSession)
class SquashSessionAdmin(admin.ModelAdmin):
	list_display = ("date_played", "created_at", "updated_at")
	date_hierarchy = "date_played"


@admin.register(SquashPlayer)
class SquashPlayerAdmin(admin.ModelAdmin):
	list_display = ("name",)
	search_fields = ("name",)


@admin.register(SquashSet)
class SquashSetAdmin(admin.ModelAdmin):
	list_display = ("match", "set_number", "player_1_points", "player_2_points")
	list_filter = ("match__date_played",)
