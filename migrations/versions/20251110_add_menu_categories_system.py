"""Add Menu, Categoria, EtiquetaEspecial, RedSocial, FotoLugar tables and extend LugarSugerido

Revision ID: 20251110_menu_cats
Revises: ef4c83ab19f0
Create Date: 2025-11-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251110_menu_cats'
down_revision = 'ef4c83ab19f0'
branch_labels = None
depends_on = None


def upgrade():
    # Crear tabla categorias
    op.create_table('categorias',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=50), nullable=False),
        sa.Column('slug', sa.String(length=50), nullable=False),
        sa.Column('icono', sa.String(length=50), nullable=True),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=True),
        sa.Column('orden', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nombre'),
        sa.UniqueConstraint('slug')
    )

    # Crear tabla etiquetas_especiales
    op.create_table('etiquetas_especiales',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=50), nullable=False),
        sa.Column('slug', sa.String(length=50), nullable=False),
        sa.Column('icono', sa.String(length=50), nullable=True),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nombre'),
        sa.UniqueConstraint('slug')
    )

    # Crear tabla menus
    op.create_table('menus',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lugar_id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('archivo_url', sa.String(length=300), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=True),
        sa.Column('orden', sa.Integer(), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=True),
        sa.Column('fecha_actualizacion', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['lugar_id'], ['lugar_sugerido.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Crear tabla items_menu
    op.create_table('items_menu',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('menu_id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=150), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('precio', sa.Float(), nullable=True),
        sa.Column('categoria_item', sa.String(length=50), nullable=True),
        sa.Column('imagen_url', sa.String(length=300), nullable=True),
        sa.Column('disponible', sa.Boolean(), nullable=True),
        sa.Column('orden', sa.Integer(), nullable=True),
        sa.Column('etiquetas_item', sa.String(length=200), nullable=True),
        sa.ForeignKeyConstraint(['menu_id'], ['menus.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Crear tabla redes_sociales
    op.create_table('redes_sociales',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lugar_id', sa.Integer(), nullable=False),
        sa.Column('tipo', sa.String(length=50), nullable=False),
        sa.Column('url_perfil', sa.String(length=300), nullable=False),
        sa.Column('qr_code_url', sa.String(length=300), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=True),
        sa.Column('clics', sa.Integer(), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['lugar_id'], ['lugar_sugerido.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Crear tabla fotos_lugar
    op.create_table('fotos_lugar',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lugar_id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(length=300), nullable=False),
        sa.Column('descripcion', sa.String(length=200), nullable=True),
        sa.Column('es_principal', sa.Boolean(), nullable=True),
        sa.Column('orden', sa.Integer(), nullable=True),
        sa.Column('fecha_subida', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['lugar_id'], ['lugar_sugerido.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Crear tablas de asociación many-to-many
    op.create_table('lugar_categorias',
        sa.Column('lugar_id', sa.Integer(), nullable=False),
        sa.Column('categoria_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['categoria_id'], ['categorias.id'], ),
        sa.ForeignKeyConstraint(['lugar_id'], ['lugar_sugerido.id'], ),
        sa.PrimaryKeyConstraint('lugar_id', 'categoria_id')
    )

    op.create_table('lugar_etiquetas',
        sa.Column('lugar_id', sa.Integer(), nullable=False),
        sa.Column('etiqueta_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['etiqueta_id'], ['etiquetas_especiales.id'], ),
        sa.ForeignKeyConstraint(['lugar_id'], ['lugar_sugerido.id'], ),
        sa.PrimaryKeyConstraint('lugar_id', 'etiqueta_id')
    )

    # Agregar nuevas columnas a lugar_sugerido
    with op.batch_alter_table('lugar_sugerido', schema=None) as batch_op:
        batch_op.add_column(sa.Column('descripcion', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('telefono', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('email_contacto', sa.String(length=150), nullable=True))
        batch_op.add_column(sa.Column('sitio_web', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('vistas', sa.Integer(), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('clics_como_llegar', sa.Integer(), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('clics_telefono', sa.Integer(), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('horarios', sa.Text(), nullable=True))

    # Agregar nuevas columnas a usuarios
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.add_column(sa.Column('plan', sa.String(length=20), nullable=True, server_default='gratuito'))
        batch_op.add_column(sa.Column('fecha_expiracion_plan', sa.Date(), nullable=True))


def downgrade():
    # Eliminar columnas de usuarios
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.drop_column('fecha_expiracion_plan')
        batch_op.drop_column('plan')

    # Eliminar columnas de lugar_sugerido
    with op.batch_alter_table('lugar_sugerido', schema=None) as batch_op:
        batch_op.drop_column('horarios')
        batch_op.drop_column('clics_telefono')
        batch_op.drop_column('clics_como_llegar')
        batch_op.drop_column('vistas')
        batch_op.drop_column('sitio_web')
        batch_op.drop_column('email_contacto')
        batch_op.drop_column('telefono')
        batch_op.drop_column('descripcion')

    # Eliminar tablas de asociación
    op.drop_table('lugar_etiquetas')
    op.drop_table('lugar_categorias')

    # Eliminar tablas nuevas
    op.drop_table('fotos_lugar')
    op.drop_table('redes_sociales')
    op.drop_table('items_menu')
    op.drop_table('menus')
    op.drop_table('etiquetas_especiales')
    op.drop_table('categorias')
