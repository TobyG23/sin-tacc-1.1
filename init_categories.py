"""
Script para inicializar categorías y etiquetas especiales en la base de datos
Ejecutar después de aplicar las migraciones con: python init_categories.py
"""
import os
from dotenv import load_dotenv
load_dotenv()

from app import app, db
from models import Categoria, EtiquetaEspecial

def init_categories():
    """Inicializa las categorías base del sistema"""
    categorias = [
        {
            'nombre': 'Restaurante',
            'slug': 'restaurante',
            'icono': 'restaurant',
            'color': '#e74c3c',
            'descripcion': 'Restaurantes y comedores',
            'orden': 1
        },
        {
            'nombre': 'Cafetería',
            'slug': 'cafeteria',
            'icono': 'coffee',
            'color': '#8e44ad',
            'descripcion': 'Cafeterías y coffee shops',
            'orden': 2
        },
        {
            'nombre': 'Panadería',
            'slug': 'panaderia',
            'icono': 'bread',
            'color': '#d68910',
            'descripcion': 'Panaderías y pastelerías',
            'orden': 3
        },
        {
            'nombre': 'Pizzería',
            'slug': 'pizzeria',
            'icono': 'pizza',
            'color': '#c0392b',
            'descripcion': 'Pizzerías',
            'orden': 4
        },
        {
            'nombre': 'Heladería',
            'slug': 'heladeria',
            'icono': 'ice-cream',
            'color': '#3498db',
            'descripcion': 'Heladerías y gelaterías',
            'orden': 5
        },
        {
            'nombre': 'Bar',
            'slug': 'bar',
            'icono': 'wine-glass',
            'color': '#16a085',
            'descripcion': 'Bares y pubs',
            'orden': 6
        },
        {
            'nombre': 'Fast Food',
            'slug': 'fast-food',
            'icono': 'burger',
            'color': '#e67e22',
            'descripcion': 'Comida rápida',
            'orden': 7
        },
        {
            'nombre': 'Tienda de Alimentos',
            'slug': 'tienda-alimentos',
            'icono': 'shopping-basket',
            'color': '#27ae60',
            'descripcion': 'Tiendas de alimentos especiales y dietéticas',
            'orden': 8
        },
        {
            'nombre': 'Supermercado',
            'slug': 'supermercado',
            'icono': 'shopping-cart',
            'color': '#2980b9',
            'descripcion': 'Supermercados',
            'orden': 9
        },
        {
            'nombre': 'Hotel',
            'slug': 'hotel',
            'icono': 'hotel',
            'color': '#34495e',
            'descripcion': 'Hoteles con opciones gastronómicas',
            'orden': 10
        },
        {
            'nombre': 'Catering',
            'slug': 'catering',
            'icono': 'utensils',
            'color': '#95a5a6',
            'descripcion': 'Servicios de catering',
            'orden': 11
        },
        {
            'nombre': 'Otro',
            'slug': 'otro',
            'icono': 'store',
            'color': '#7f8c8d',
            'descripcion': 'Otros comercios',
            'orden': 99
        }
    ]

    with app.app_context():
        for cat_data in categorias:
            # Verificar si ya existe
            existing = Categoria.query.filter_by(slug=cat_data['slug']).first()
            if not existing:
                categoria = Categoria(**cat_data)
                db.session.add(categoria)
                print(f"✓ Categoría creada: {cat_data['nombre']}")
            else:
                print(f"- Categoría ya existe: {cat_data['nombre']}")

        db.session.commit()
        print(f"\n{len(categorias)} categorías inicializadas correctamente")


def init_etiquetas():
    """Inicializa las etiquetas especiales del sistema"""
    etiquetas = [
        {
            'nombre': 'Sin Gluten / Apto Celíacos',
            'slug': 'sin-gluten',
            'icono': 'wheat-slash',
            'color': '#f39c12',
            'descripcion': 'Opciones sin gluten, aptas para celíacos'
        },
        {
            'nombre': 'Vegano',
            'slug': 'vegano',
            'icono': 'leaf',
            'color': '#27ae60',
            'descripcion': 'Opciones veganas, sin productos animales'
        },
        {
            'nombre': 'Vegetariano',
            'slug': 'vegetariano',
            'icono': 'carrot',
            'color': '#2ecc71',
            'descripcion': 'Opciones vegetarianas'
        },
        {
            'nombre': 'Sin Lactosa',
            'slug': 'sin-lactosa',
            'icono': 'milk-off',
            'color': '#3498db',
            'descripcion': 'Opciones sin lactosa'
        },
        {
            'nombre': 'Sin Azúcar',
            'slug': 'sin-azucar',
            'icono': 'candy',
            'color': '#9b59b6',
            'descripcion': 'Opciones sin azúcar, aptas para diabéticos'
        },
        {
            'nombre': 'Kosher',
            'slug': 'kosher',
            'icono': 'star-of-david',
            'color': '#1abc9c',
            'descripcion': 'Comida kosher'
        },
        {
            'nombre': 'Halal',
            'slug': 'halal',
            'icono': 'moon',
            'color': '#16a085',
            'descripcion': 'Comida halal'
        },
        {
            'nombre': 'Orgánico',
            'slug': 'organico',
            'icono': 'seedling',
            'color': '#27ae60',
            'descripcion': 'Productos orgánicos'
        },
        {
            'nombre': 'Pet Friendly',
            'slug': 'pet-friendly',
            'icono': 'paw',
            'color': '#e67e22',
            'descripcion': 'Permite mascotas'
        },
        {
            'nombre': 'Accesible',
            'slug': 'accesible',
            'icono': 'wheelchair',
            'color': '#3498db',
            'descripcion': 'Acceso para personas con movilidad reducida'
        },
        {
            'nombre': 'WiFi Gratis',
            'slug': 'wifi-gratis',
            'icono': 'wifi',
            'color': '#9b59b6',
            'descripcion': 'WiFi gratuito disponible'
        },
        {
            'nombre': 'Delivery',
            'slug': 'delivery',
            'icono': 'truck',
            'color': '#e74c3c',
            'descripcion': 'Servicio de delivery'
        },
        {
            'nombre': 'Para Llevar',
            'slug': 'para-llevar',
            'icono': 'shopping-bag',
            'color': '#f39c12',
            'descripcion': 'Servicio para llevar / take away'
        }
    ]

    with app.app_context():
        for etiq_data in etiquetas:
            # Verificar si ya existe
            existing = EtiquetaEspecial.query.filter_by(slug=etiq_data['slug']).first()
            if not existing:
                etiqueta = EtiquetaEspecial(**etiq_data)
                db.session.add(etiqueta)
                print(f"✓ Etiqueta creada: {etiq_data['nombre']}")
            else:
                print(f"- Etiqueta ya existe: {etiq_data['nombre']}")

        db.session.commit()
        print(f"\n{len(etiquetas)} etiquetas inicializadas correctamente")


def migrate_existing_data():
    """
    Migra los datos existentes:
    - Asigna categoría "Otro" a todos los lugares sin categoría
    - Asigna etiqueta "Sin Gluten" a todos los lugares existentes
    """
    with app.app_context():
        from models import LugarSugerido

        # Obtener categoría "Otro" y etiqueta "Sin Gluten"
        categoria_otro = Categoria.query.filter_by(slug='otro').first()
        etiqueta_sin_gluten = EtiquetaEspecial.query.filter_by(slug='sin-gluten').first()

        if not categoria_otro or not etiqueta_sin_gluten:
            print("Error: Categorías o etiquetas no encontradas. Ejecuta primero init_categories() e init_etiquetas()")
            return

        # Obtener todos los lugares
        lugares = LugarSugerido.query.all()

        for lugar in lugares:
            # Asignar categoría si no tiene
            if not lugar.categorias:
                lugar.categorias.append(categoria_otro)
                print(f"✓ Categoría 'Otro' asignada a: {lugar.nombre}")

            # Asignar etiqueta sin gluten si no tiene
            if not lugar.etiquetas:
                lugar.etiquetas.append(etiqueta_sin_gluten)
                print(f"✓ Etiqueta 'Sin Gluten' asignada a: {lugar.nombre}")

        db.session.commit()
        print(f"\n{len(lugares)} lugares migrados correctamente")


if __name__ == '__main__':
    print("=" * 60)
    print("INICIALIZACIÓN DE CATEGORÍAS Y ETIQUETAS - LocalHub")
    print("=" * 60)
    print()

    # Inicializar categorías
    print("1. Inicializando categorías...")
    print("-" * 60)
    init_categories()
    print()

    # Inicializar etiquetas
    print("2. Inicializando etiquetas especiales...")
    print("-" * 60)
    init_etiquetas()
    print()

    # Migrar datos existentes
    print("3. Migrando datos existentes...")
    print("-" * 60)
    migrate_existing_data()
    print()

    print("=" * 60)
    print("✓ INICIALIZACIÓN COMPLETADA")
    print("=" * 60)
