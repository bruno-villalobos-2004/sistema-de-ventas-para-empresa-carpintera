import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import os
import json
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import tempfile
from datetime import timedelta

class MiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Carpintería - Iglomar")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f0f0f0')
        
        # Colores de la empresa
        self.colores = {
            'gris_oscuro': '#4a4a4a',
            'gris_medio': '#6c6c6c',
            'gris_claro': '#e0e0e0',
            'vino': '#8B1A1A',
            'vino_claro': '#A52A2A',
            'vino_suave': '#C41E3A',
            'blanco': '#ffffff',
            'gris_fondo': '#f5f5f5'
        }
        
        # Crear carpetas necesarias
        self.crear_carpetas()
        
        self.setup_styles()
        self.cargar_logo()
        
        self.archivo_datos = "datos_administracion.json"
        self.cargar_datos()
        
        self.presupuestos = []
        self.presupuesto_actual = []
        
        self.materiales_venta = []
        self.costo_fabricacion = tk.StringVar()
        self.tiempo_elaboracion = tk.StringVar()
        self.nomina_base = tk.StringVar()
        
        self.create_header()
        self.create_main_buttons()
    
    def crear_carpetas(self):
        """Crear las carpetas necesarias para almacenar archivos"""
        carpetas = ['facturas_txt', 'facturas_pdf', 'presupuestos_txt', 'reportes']
        for carpeta in carpetas:
            if not os.path.exists(carpeta):
                os.makedirs(carpeta)
    
    def cargar_logo(self):
        """Cargar el logo de la empresa"""
        try:
            logo_path = "logo_iglomar.png"
            if os.path.exists(logo_path):
                imagen = Image.open(logo_path)
                imagen = imagen.resize((140, 100), Image.Resampling.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(imagen)
            else:
                self.logo_img = None
        except Exception as e:
            print(f"No se pudo cargar el logo: {e}")
            self.logo_img = None
    
    def setup_styles(self):
        """Configurar estilos para la aplicación"""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Main.TButton', font=('Arial', 11, 'bold'), padding=10,
                       background=self.colores['vino'], foreground='white')
        style.map('Main.TButton',
                  background=[('active', self.colores['vino_claro']),
                             ('pressed', self.colores['gris_oscuro'])])
        
        style.configure('Treeview', font=('Arial', 10), rowheight=25,
                       background=self.colores['blanco'],
                       fieldbackground=self.colores['blanco'])
        style.configure('Treeview.Heading', font=('Arial', 11, 'bold'),
                       background=self.colores['gris_medio'],
                       foreground='white')
        style.map('Treeview.Heading',
                  background=[('active', self.colores['vino'])])
        
        style.configure('TNotebook', background=self.colores['gris_fondo'])
        style.configure('TNotebook.Tab', font=('Arial', 10, 'bold'), padding=[10, 5],
                       background=self.colores['gris_claro'])
        style.map('TNotebook.Tab',
                  background=[('selected', self.colores['vino'])],
                  foreground=[('selected', 'white')])
        
        style.configure('TLabelframe', background=self.colores['gris_fondo'],
                       borderwidth=2, relief='solid')
        style.configure('TLabelframe.Label', font=('Arial', 11, 'bold'),
                       foreground=self.colores['vino'])
    
    def create_header(self):
        """Crear encabezado con logo y título"""
        header_frame = tk.Frame(self.root, bg=self.colores['gris_oscuro'], height=120)
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)
        
        logo_left = tk.Label(header_frame, text="🪚", font=("Arial", 52), 
                            bg=self.colores['gris_oscuro'], fg=self.colores['vino_claro'])
        logo_left.pack(side="left", padx=20, pady=10)
        
        titulo_frame = tk.Frame(header_frame, bg=self.colores['gris_oscuro'])
        titulo_frame.pack(side="left", expand=True, fill="both")
        
        tk.Label(titulo_frame, text="MADERAS IGLOMAR", 
                font=("Arial", 22, "bold"), bg=self.colores['gris_oscuro'], 
                fg=self.colores['gris_claro']).pack(expand=True)
        tk.Label(titulo_frame, text="Sistema Integral de Gestión", 
                font=("Arial", 12), bg=self.colores['gris_oscuro'], 
                fg=self.colores['gris_claro']).pack(expand=True)
        
        if self.logo_img:
            logo_label = tk.Label(header_frame, image=self.logo_img, 
                                 bg=self.colores['gris_oscuro'])
            logo_label.pack(side="right", padx=20, pady=10)
        else:
            logo_frame = tk.Frame(header_frame, bg=self.colores['vino'], 
                                 width=80, height=80, relief=tk.RAISED, bd=2)
            logo_frame.pack(side="right", padx=20, pady=10)
            logo_frame.pack_propagate(False)
            tk.Label(logo_frame, text="IGLOMAR", font=("Arial", 10, "bold"),
                    bg=self.colores['vino'], fg='white', wraplength=70).pack(expand=True)
        
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        tk.Label(header_frame, text=fecha_actual, font=("Arial", 11, "bold"), 
                bg=self.colores['gris_oscuro'], fg=self.colores['gris_claro']).pack(side="right", padx=20)
    
    def create_main_buttons(self):
        """Crear botones principales del menú"""
        main_frame = tk.Frame(self.root, bg=self.colores['gris_fondo'])
        main_frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        buttons = [
            ("📊 MÓDULO DE PRESUPUESTOS", self.modulo_presupuestos, self.colores['vino']),
            ("💰 MÓDULO DE VENTAS", self.modulo_ventas, self.colores['vino_claro']),
            ("📋 MÓDULO DE ADMINISTRACIÓN", self.modulo_administracion, self.colores['vino']),
            ("🔍 BUSCAR PRESUPUESTO", self.buscar_presupuesto_para_facturar, self.colores['vino_suave']),
            ("📈 REPORTES", self.modulo_reportes, self.colores['gris_oscuro'])
        ]
        
        for i, (text, command, color) in enumerate(buttons):
            btn = tk.Button(main_frame, text=text, command=command,
                           bg=color, fg="white", font=("Arial", 12, "bold"),
                           height=3, width=12, relief="raised", bd=2,
                           activebackground=self.colores['vino_claro'],
                           activeforeground='white')
            btn.grid(row=i//2, column=i%2, padx=20, pady=20, sticky="nsew")
        
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
    
    def cargar_datos(self):
        """Cargar datos de administración desde archivo JSON"""
        if os.path.exists(self.archivo_datos):
            try:
                with open(self.archivo_datos, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                    self.facturas = datos.get('facturas', [])
                    self.gastos = datos.get('gastos', [])
                    self.presupuestos = datos.get('presupuestos', [])
                    self.proveedores = datos.get('proveedores', [])
            except:
                self.facturas = []
                self.gastos = []
                self.presupuestos = []
                self.proveedores = []
        else:
            self.facturas = []
            self.gastos = []
            self.presupuestos = []
            self.proveedores = []
    
    def guardar_datos(self):
        """Guardar datos de administración en archivo JSON"""
        datos = {
            'facturas': self.facturas,
            'gastos': self.gastos,
            'presupuestos': self.presupuestos,
            'proveedores': self.proveedores
        }
        with open(self.archivo_datos, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
    
    def generar_pdf_factura(self, factura, materiales_data, total_materiales, costo_nomina, 
                            costo_fabricacion, costo_transporte, costo_instalacion):
        """Generar factura en PDF con formato profesional"""
        fecha = datetime.now()
        nombre_archivo = f"facturas_pdf/factura_{factura['id']}.pdf"
        
        doc = SimpleDocTemplate(nombre_archivo, pagesize=letter,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=72)
        
        styles = getSampleStyleSheet()
        story = []
        
        # Estilos personalizados
        estilo_titulo = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#8B1A1A'),
            alignment=TA_CENTER,
            spaceAfter=30
        )
        
        estilo_subtitulo = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#4a4a4a'),
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        estilo_empresa = ParagraphStyle(
            'EmpresaStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#6c6c6c'),
            alignment=TA_CENTER
        )
        
        estilo_seccion = ParagraphStyle(
            'SeccionStyle',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#8B1A1A'),
            spaceAfter=10,
            spaceBefore=20
        )
        
        # Encabezado de la empresa
        story.append(Paragraph("IGLOMAR MUEBLES", estilo_titulo))
        story.append(Paragraph("Carpintería y Mobiliario de Calidad", estilo_empresa))
        story.append(Paragraph("RIF: J-50190227-5", estilo_empresa))
        story.append(Paragraph("Urb. La Paz, AV. 97-A, CASA # 47-06", estilo_empresa))
        story.append(Paragraph("Teléfonos: 0424-6059984 / 0424-6824212", estilo_empresa))
        story.append(Paragraph("Email: iglomarmuebles@gmail.com", estilo_empresa))
        story.append(Spacer(1, 20))
        
        # Línea separadora
        story.append(Paragraph("━" * 70, estilo_empresa))
        
        # Título FACTURA
        story.append(Paragraph(f"FACTURA DE VENTA", estilo_subtitulo))
        story.append(Paragraph(f"Nº: {factura['id']}", estilo_empresa))
        story.append(Paragraph(f"Fecha: {factura['fecha']}", estilo_empresa))
        story.append(Spacer(1, 20))
        
        # Datos del cliente
        story.append(Paragraph("DATOS DEL CLIENTE", estilo_seccion))
        
        datos_cliente = [
            ["Nombre:", factura['cliente']],
            ["Teléfono:", factura.get('telefono', '')],
            ["Email:", factura.get('email', '')],
            ["Dirección:", factura.get('direccion', '')]
        ]
        
        tabla_cliente = Table(datos_cliente, colWidths=[100, 350])
        tabla_cliente.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#8B1A1A')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(tabla_cliente)
        story.append(Spacer(1, 15))
        
        # Tabla de materiales
        story.append(Paragraph("DETALLE DE MATERIALES", estilo_seccion))
        
        tabla_materiales_data = [["Descripción", "Cantidad", "Precio Unitario", "Precio Total"]]
        for item in materiales_data:
            tabla_materiales_data.append([
                item['material'], 
                str(item['cantidad']), 
                item['precio_unitario'], 
                item['precio_total']
            ])
        
        tabla_materiales = Table(tabla_materiales_data, colWidths=[250, 80, 100, 100])
        tabla_materiales.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8B1A1A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f5f5')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0'))
        ]))
        story.append(tabla_materiales)
        story.append(Spacer(1, 15))
        
        # Resumen de costos
        story.append(Paragraph("RESUMEN DE COSTOS", estilo_seccion))
        
        costos_data = [
            ["Total Materiales:", f"${total_materiales:.2f}"],
            ["Total de Fabricación:", f"${(total_materiales * 1.30) + float(costo_nomina.replace('$', '').replace(',', '')):.2f}"],
            [""],
            ["Costo de Transporte:", costo_transporte],
            ["Costo de Instalación:", costo_instalacion],
        ]
        
        tabla_costos = Table(costos_data, colWidths=[200, 200])
        tabla_costos.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#4a4a4a')),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(tabla_costos)
        story.append(Spacer(1, 20))
        
        # Línea separadora
        story.append(Paragraph("━" * 70, estilo_empresa))
        
        # Total y pago
        story.append(Spacer(1, 10))
        
        total_data = [
            ["TOTAL FACTURA:", f"${factura['total']:.2f}"],
            ["ABONO:", f"${factura['abono']:.2f}"],
            ["SALDO PENDIENTE:", f"${factura['saldo']:.2f}"],
            ["ESTADO:", factura['estado']],
        ]
        
        tabla_total = Table(total_data, colWidths=[200, 200])
        tabla_total.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#8B1A1A')),
            ('TEXTCOLOR', (1, 0), (1, 2), colors.HexColor('#8B1A1A')),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(tabla_total)
        story.append(Spacer(1, 20))
        
        # Notas
        story.append(Paragraph("NOTAS IMPORTANTES", estilo_seccion))
        notas = """
        - El pago puede realizarse en efectivo, Zelle, transferencia bancaria o Binance.<br/>
        - Este documento tiene validez como comprobante de pago.<br/>
        - Los muebles cuentan con garantía de 6 meses contra defectos de fabricación.<br/>
        - El tiempo de elaboración es de 16 días hábiles aproximadamente.
        """
        story.append(Paragraph(notas, styles['Normal']))
        
        # Pie de página
        story.append(Spacer(1, 30))
        story.append(Paragraph("Gracias por su confianza", estilo_empresa))
        story.append(Paragraph("Madera Iglomar - Calidad y Garantía", estilo_empresa))
        
        # Generar PDF
        doc.build(story)
        return nombre_archivo
    
    def buscar_presupuesto_para_facturar(self):
        """Módulo para buscar presupuestos y convertirlos en factura"""
        ventana = tk.Toplevel(self.root)
        ventana.title("Buscar Presupuesto - Maderas Iglomar")
        ventana.geometry("900x600")
        ventana.configure(bg=self.colores['gris_fondo'])
        
        titulo = tk.Label(ventana, text="BUSCAR PRESUPUESTO PARA FACTURAR", 
                         font=("Arial", 16, "bold"), bg=self.colores['gris_fondo'], 
                         fg=self.colores['vino'])
        titulo.pack(pady=20)
        
        frame_busqueda = tk.Frame(ventana, bg=self.colores['blanco'], relief=tk.RAISED, bd=2)
        frame_busqueda.pack(pady=20, padx=20, fill="x")
        
        tk.Label(frame_busqueda, text="Buscar por:", font=("Arial", 11), 
                bg=self.colores['blanco'], fg=self.colores['gris_oscuro']).pack(side=tk.LEFT, padx=10)
        
        busqueda_var = tk.StringVar()
        tk.Entry(frame_busqueda, textvariable=busqueda_var, width=40, 
                font=("Arial", 11)).pack(side=tk.LEFT, padx=10)
        
        columns = ("ID", "Fecha", "Cliente", "Total", "Estado")
        tree_presupuestos = ttk.Treeview(ventana, columns=columns, show="headings", height=10)
        
        for col in columns:
            tree_presupuestos.heading(col, text=col)
            if col == "ID":
                tree_presupuestos.column(col, width=150)
            elif col == "Cliente":
                tree_presupuestos.column(col, width=250)
            else:
                tree_presupuestos.column(col, width=150)
        
        tree_presupuestos.pack(pady=10, padx=20, fill="both", expand=True)
        
        def cargar_presupuestos():
            for item in tree_presupuestos.get_children():
                tree_presupuestos.delete(item)
            
            busqueda = busqueda_var.get().lower()
            for presupuesto in self.presupuestos:
                if presupuesto.get('estado') == 'PENDIENTE':
                    if busqueda and busqueda not in presupuesto.get('cliente', '').lower():
                        continue
                    tree_presupuestos.insert("", "end", values=(
                        presupuesto['id'],
                        presupuesto['fecha'],
                        presupuesto['cliente'],
                        f"${presupuesto['total']:.2f}",
                        presupuesto['estado']
                    ))
        
        def seleccionar_presupuesto():
            seleccion = tree_presupuestos.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Seleccione un presupuesto")
                return
            
            item = tree_presupuestos.item(seleccion[0])
            presupuesto_id = item['values'][0]
            
            for presupuesto in self.presupuestos:
                if presupuesto['id'] == presupuesto_id:
                    ventana.destroy()
                    self.modulo_ventas(presupuesto_cargado=presupuesto)
                    break
        
        btn_seleccionar = tk.Button(ventana, text="Facturar este Presupuesto", 
                                   command=seleccionar_presupuesto,
                                   bg=self.colores['vino'], fg="white", 
                                   font=("Arial", 12, "bold"),
                                   height=2, width=30,
                                   activebackground=self.colores['vino_claro'])
        btn_seleccionar.pack(pady=20)
        
        busqueda_var.trace('w', lambda *args: cargar_presupuestos())
        cargar_presupuestos()
    
    def agregar_material_presupuesto(self, tree, descripcion_entry, precio_entry, cantidad_entry):
        descripcion = descripcion_entry.get()
        precio = precio_entry.get()
        cantidad = cantidad_entry.get()
        
        if descripcion and precio and cantidad:
            try:
                precio = float(precio)
                cantidad = float(cantidad)
                subtotal = precio * cantidad
                tree.insert("", "end", values=(descripcion, f"${precio:.2f}", 
                                               cantidad, f"${subtotal:.2f}"))
                descripcion_entry.delete(0, tk.END)
                precio_entry.delete(0, tk.END)
                cantidad_entry.delete(0, tk.END)
            except ValueError:
                messagebox.showerror("Error", "Precio y cantidad deben ser números")
        else:
            messagebox.showwarning("Advertencia", "Complete todos los campos")
    
    def modulo_presupuestos(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Módulo de Presupuestos - Maderas Iglomar")
        ventana.geometry("1100x800")
        ventana.configure(bg=self.colores['gris_fondo'])
        
        titulo = tk.Label(ventana, text="CREAR NUEVO PRESUPUESTO", 
                         font=("Arial", 18, "bold"), bg=self.colores['gris_fondo'], 
                         fg=self.colores['vino'])
        titulo.pack(pady=15)
        
        notebook = ttk.Notebook(ventana)
        notebook.pack(pady=10, padx=20, fill="both", expand=True)
        
        frame_materiales = ttk.Frame(notebook)
        notebook.add(frame_materiales, text="Materiales")
        
        columns = ("Descripción", "Precio Unitario", "Cantidad", "Subtotal")
        tree = ttk.Treeview(frame_materiales, columns=columns, show="headings", height=8)
        
        for col in columns:
            tree.heading(col, text=col)
            if col == "Descripción":
                tree.column(col, width=300)
            else:
                tree.column(col, width=150)
        
        tree.pack(pady=10, padx=10, fill="both", expand=True)
        
        frame_agregar = tk.Frame(frame_materiales, bg=self.colores['gris_fondo'])
        frame_agregar.pack(pady=10)
        
        tk.Label(frame_agregar, text="Descripción:", bg=self.colores['gris_fondo'], 
                font=("Arial", 10), fg=self.colores['gris_oscuro']).grid(row=0, column=0, padx=5)
        descripcion_entry = tk.Entry(frame_agregar, width=25, font=("Arial", 10))
        descripcion_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(frame_agregar, text="Precio:", bg=self.colores['gris_fondo'], 
                font=("Arial", 10), fg=self.colores['gris_oscuro']).grid(row=0, column=2, padx=5)
        precio_entry = tk.Entry(frame_agregar, width=15, font=("Arial", 10))
        precio_entry.grid(row=0, column=3, padx=5)
        
        tk.Label(frame_agregar, text="Cantidad:", bg=self.colores['gris_fondo'], 
                font=("Arial", 10), fg=self.colores['gris_oscuro']).grid(row=0, column=4, padx=5)
        cantidad_entry = tk.Entry(frame_agregar, width=10, font=("Arial", 10))
        cantidad_entry.grid(row=0, column=5, padx=5)
        
        frame_fabricacion = ttk.Frame(notebook)
        notebook.add(frame_fabricacion, text="Costos de Fabricación y Nómina")
        
        costo_materiales_var = tk.StringVar()
        tiempo_elab_var = tk.StringVar()
        mano_obra_diaria_var = tk.StringVar()
        costo_nomina_var = tk.StringVar()
        porcentaje_var = tk.StringVar()
        costo_fabricacion_var = tk.StringVar()
        
        tk.Label(frame_fabricacion, text="Costo de Materiales:", font=("Arial", 11),
                fg=self.colores['gris_oscuro']).pack(pady=5)
        tk.Entry(frame_fabricacion, textvariable=costo_materiales_var, state='readonly', 
                width=20, font=("Arial", 11)).pack(pady=5)
        
        tk.Label(frame_fabricacion, text="+30% sobre materiales:", font=("Arial", 11),
                fg=self.colores['vino']).pack(pady=5)
        porcentaje_materiales_var = tk.StringVar()
        tk.Label(frame_fabricacion, textvariable=porcentaje_materiales_var, font=("Arial", 12, "bold"),
                fg=self.colores['vino']).pack(pady=5)
        
        tk.Label(frame_fabricacion, text="Tiempo de Elaboración (días):", font=("Arial", 11),
                fg=self.colores['gris_oscuro']).pack(pady=5)
        tiempo_entry = tk.Entry(frame_fabricacion, textvariable=tiempo_elab_var, width=20, font=("Arial", 11))
        tiempo_entry.pack(pady=5)
        
        tk.Label(frame_fabricacion, text="Mano de Obra Diaria ($):", font=("Arial", 11),
                fg=self.colores['gris_oscuro']).pack(pady=5)
        mano_obra_frame = tk.Frame(frame_fabricacion, bg=self.colores['gris_fondo'])
        mano_obra_frame.pack(pady=5)
        
        mano_obra_opciones = ["80", "85", "90", "95", "100"]
        mano_obra_combo = ttk.Combobox(mano_obra_frame, values=mano_obra_opciones, width=10, font=("Arial", 11))
        mano_obra_combo.set("90")
        mano_obra_combo.pack(side=tk.LEFT, padx=5)
        tk.Label(mano_obra_frame, text="$ por día", font=("Arial", 11),
                bg=self.colores['gris_fondo']).pack(side=tk.LEFT)
        
        tk.Label(frame_fabricacion, text="Costo Total de Nómina:", font=("Arial", 11),
                fg=self.colores['gris_oscuro']).pack(pady=5)
        tk.Entry(frame_fabricacion, textvariable=costo_nomina_var, state='readonly', 
                width=20, font=("Arial", 11)).pack(pady=5)
        
        tk.Label(frame_fabricacion, text="Porcentaje de Ganancia:", font=("Arial", 11),
                fg=self.colores['gris_oscuro']).pack(pady=5)
        porcentaje_opciones = ["10%", "15%", "20%", "25%", "30%", "35%", "40%", "45%", "50%"]
        porcentaje_combo = ttk.Combobox(frame_fabricacion, values=porcentaje_opciones, width=15, font=("Arial", 11))
        porcentaje_combo.set("20%")
        porcentaje_combo.pack(pady=5)
        
        frame_adicionales = ttk.Frame(notebook)
        notebook.add(frame_adicionales, text="Costos Adicionales")
        
        costo_transporte_var = tk.StringVar()
        costo_instalacion_var = tk.StringVar()
        costo_adicional_total_var = tk.StringVar()
        
        tk.Label(frame_adicionales, text="Costo de Transporte ($):", font=("Arial", 11),
                fg=self.colores['gris_oscuro']).pack(pady=10)
        tk.Entry(frame_adicionales, textvariable=costo_transporte_var, width=20, font=("Arial", 11)).pack(pady=5)
        
        tk.Label(frame_adicionales, text="Costo de Instalación ($):", font=("Arial", 11),
                fg=self.colores['gris_oscuro']).pack(pady=10)
        tk.Entry(frame_adicionales, textvariable=costo_instalacion_var, width=20, font=("Arial", 11)).pack(pady=5)
        
        frame_cliente = tk.LabelFrame(ventana, text="DATOS DEL CLIENTE", 
                                     font=("Arial", 12, "bold"), bg=self.colores['gris_fondo'], 
                                     fg=self.colores['vino'], padx=10, pady=10)
        frame_cliente.pack(pady=10, padx=20, fill="x")
        
        tk.Label(frame_cliente, text="Nombre del Cliente:", bg=self.colores['gris_fondo'], 
                font=("Arial", 10), fg=self.colores['gris_oscuro']).grid(row=0, column=0, padx=5, pady=5)
        nombre_cliente_var = tk.StringVar()
        tk.Entry(frame_cliente, textvariable=nombre_cliente_var, width=30, font=("Arial", 10)).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(frame_cliente, text="Teléfono:", bg=self.colores['gris_fondo'], 
                font=("Arial", 10), fg=self.colores['gris_oscuro']).grid(row=0, column=2, padx=5, pady=5)
        telefono_var = tk.StringVar()
        tk.Entry(frame_cliente, textvariable=telefono_var, width=20, font=("Arial", 10)).grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(frame_cliente, text="Email:", bg=self.colores['gris_fondo'], 
                font=("Arial", 10), fg=self.colores['gris_oscuro']).grid(row=0, column=4, padx=5, pady=5)
        email_var = tk.StringVar()
        tk.Entry(frame_cliente, textvariable=email_var, width=25, font=("Arial", 10)).grid(row=0, column=5, padx=5, pady=5)
        
        frame_total = tk.Frame(ventana, bg=self.colores['gris_fondo'])
        frame_total.pack(pady=10)
        
        total_label = tk.Label(frame_total, text="Total Presupuesto: $0.00", 
                              font=("Arial", 16, "bold"), bg=self.colores['gris_fondo'], 
                              fg=self.colores['vino'])
        total_label.pack()
        
        def calcular_total():
            total_materiales = 0
            for item in tree.get_children():
                values = tree.item(item)['values']
                if values and len(values) > 3:
                    subtotal_str = values[3].replace('$', '')
                    try:
                        total_materiales += float(subtotal_str)
                    except:
                        pass
            
            costo_materiales_var.set(f"${total_materiales:.2f}")
            
            porcentaje_30 = total_materiales * 0.30
            porcentaje_materiales_var.set(f"+30%: ${porcentaje_30:.2f}")
            
            try:
                tiempo = float(tiempo_elab_var.get() if tiempo_elab_var.get() else 0)
                mano_obra_diaria = float(mano_obra_combo.get() if mano_obra_combo.get() else 90)
                costo_nomina = mano_obra_diaria * tiempo
                costo_nomina_var.set(f"${costo_nomina:.2f}")
            except:
                costo_nomina = 0
                costo_nomina_var.set("$0.00")
            
            costo_fab = total_materiales + porcentaje_30 + costo_nomina
            
            try:
                porcentaje_str = porcentaje_combo.get()
                if porcentaje_str != "Seleccione porcentaje" and porcentaje_str:
                    porcentaje = float(porcentaje_str.replace('%', '')) / 100
                    ganancia = costo_fab * porcentaje
                else:
                    ganancia = 0
                costo_con_ganancia = costo_fab + ganancia
                costo_fabricacion_var.set(f"${costo_con_ganancia:.2f}")
            except:
                costo_con_ganancia = costo_fab
                costo_fabricacion_var.set(f"${costo_fab:.2f}")
            
            try:
                costo_transporte = float(costo_transporte_var.get() if costo_transporte_var.get() else 0)
                costo_instalacion = float(costo_instalacion_var.get() if costo_instalacion_var.get() else 0)
                costo_adicional_total = costo_transporte + costo_instalacion
                costo_adicional_total_var.set(f"${costo_adicional_total:.2f}")
            except:
                costo_adicional_total = 0
                costo_adicional_total_var.set("$0.00")
            
            total = costo_con_ganancia + costo_adicional_total
            total_label.config(text=f"Total Presupuesto: ${total:.2f}")
            return total
        
        def guardar_presupuesto():
            total = calcular_total()
            nombre_cliente = nombre_cliente_var.get()
            
            if total > 0 and nombre_cliente:
                fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
                presupuesto_id = f"P-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                materiales = []
                for item in tree.get_children():
                    values = tree.item(item)['values']
                    if values:
                        materiales.append({
                            'descripcion': values[0],
                            'precio_unitario': values[1],
                            'cantidad': values[2],
                            'subtotal': values[3]
                        })
                
                presupuesto = {
                    'id': presupuesto_id,
                    'cliente': nombre_cliente,
                    'telefono': telefono_var.get(),
                    'email': email_var.get(),
                    'fecha': fecha,
                    'total': total,
                    'materiales': materiales,
                    'total_materiales': float(costo_materiales_var.get().replace('$', '')),
                    'porcentaje_30': float(porcentaje_materiales_var.get().replace('+30%: $', '')),
                    'costo_nomina': float(costo_nomina_var.get().replace('$', '')),
                    'costo_fabricacion': float(costo_fabricacion_var.get().replace('$', '')),
                    'costo_transporte': float(costo_transporte_var.get() if costo_transporte_var.get() else 0),
                    'costo_instalacion': float(costo_instalacion_var.get() if costo_instalacion_var.get() else 0),
                    'tiempo_elaboracion': tiempo_elab_var.get(),
                    'mano_obra_diaria': mano_obra_combo.get(),
                    'porcentaje_ganancia': porcentaje_combo.get(),
                    'estado': 'PENDIENTE'
                }
                
                self.presupuestos.append(presupuesto)
                self.guardar_datos()
                
                # Guardar en carpeta presupuestos_txt
                nombre_archivo = f"presupuestos_txt/presupuesto_{presupuesto_id}.txt"
                
                with open(nombre_archivo, 'w', encoding='utf-8') as f:
                    f.write("="*80 + "\n")
                    f.write("PRESUPUESTO - MADERAS IGLOMAR\n")
                    f.write("="*80 + "\n\n")
                    f.write(f"Nº PRESUPUESTO: {presupuesto_id}\n")
                    f.write(f"FECHA: {fecha}\n\n")
                    f.write("DATOS DEL CLIENTE:\n")
                    f.write("-"*80 + "\n")
                    f.write(f"Nombre: {nombre_cliente}\n")
                    f.write(f"Teléfono: {telefono_var.get()}\n")
                    f.write(f"Email: {email_var.get()}\n\n")
                    f.write("MATERIALES:\n")
                    f.write("-"*80 + "\n")
                    for material in materiales:
                        f.write(f"• {material['descripcion']}: {material['cantidad']} x {material['precio_unitario']} = {material['subtotal']}\n")
                    f.write("\nCOSTOS:\n")
                    f.write("-"*80 + "\n")
                    f.write(f"Total Materiales: ${presupuesto['total_materiales']:.2f}\n")
                    f.write(f"+30% sobre materiales: ${presupuesto['porcentaje_30']:.2f}\n")
                    f.write(f"Costo de Nómina: ${presupuesto['costo_nomina']:.2f}\n")
                    f.write(f"Subtotal Fabricación: ${presupuesto['costo_fabricacion'] - presupuesto['costo_transporte'] - presupuesto['costo_instalacion']:.2f}\n")
                    f.write(f"Ganancia: {porcentaje_combo.get()}\n")
                    f.write(f"Costo de Transporte: ${presupuesto['costo_transporte']:.2f}\n")
                    f.write(f"Costo de Instalación: ${presupuesto['costo_instalacion']:.2f}\n")
                    f.write("\n" + "="*80 + "\n")
                    f.write(f"TOTAL PRESUPUESTADO: ${total:.2f}\n")
                    f.write("="*80 + "\n")
                
                messagebox.showinfo("Éxito", f"Presupuesto guardado como {nombre_archivo}\nID: {presupuesto_id}")
                ventana.destroy()
            else:
                if total <= 0:
                    messagebox.showwarning("Advertencia", "Agregue al menos un material")
                else:
                    messagebox.showwarning("Advertencia", "Ingrese el nombre del cliente")
        
        frame_botones = tk.Frame(ventana, bg=self.colores['gris_fondo'])
        frame_botones.pack(pady=15)
        
        btn_agregar = tk.Button(frame_agregar, text="Agregar Material", 
                               command=lambda: self.agregar_material_presupuesto(tree, descripcion_entry, precio_entry, cantidad_entry),
                               bg=self.colores['vino'], fg="white", font=("Arial", 10, "bold"),
                               activebackground=self.colores['vino_claro'])
        btn_agregar.grid(row=0, column=6, padx=10)
        
        btn_calcular = tk.Button(frame_botones, text="Calcular Total", command=calcular_total,
                                bg=self.colores['gris_medio'], fg="white", font=("Arial", 11, "bold"), width=15,
                                activebackground=self.colores['gris_oscuro'])
        btn_calcular.pack(side=tk.LEFT, padx=10)
        
        btn_guardar = tk.Button(frame_botones, text="Guardar Presupuesto", command=guardar_presupuesto,
                               bg=self.colores['vino'], fg="white", font=("Arial", 11, "bold"), width=15,
                               activebackground=self.colores['vino_claro'])
        btn_guardar.pack(side=tk.LEFT, padx=10)
        
        def actualizar_calculo(*args):
            calcular_total()
        
        tiempo_elab_var.trace('w', actualizar_calculo)
        mano_obra_combo.bind('<<ComboboxSelected>>', lambda e: calcular_total())
        porcentaje_combo.bind('<<ComboboxSelected>>', lambda e: calcular_total())
        costo_transporte_var.trace('w', actualizar_calculo)
        costo_instalacion_var.trace('w', actualizar_calculo)
    
    def modulo_ventas(self, presupuesto_cargado=None):
        ventana = tk.Toplevel(self.root)
        ventana.title("Módulo de Ventas - Maderas Iglomar")
        ventana.geometry("1200x800")
        ventana.configure(bg=self.colores['gris_fondo'])
        
        titulo = tk.Label(ventana, text="FACTURACIÓN DE VENTAS", 
                         font=("Arial", 18, "bold"), bg=self.colores['gris_fondo'], 
                         fg=self.colores['vino'])
        titulo.pack(pady=15)
        
        notebook = ttk.Notebook(ventana)
        notebook.pack(pady=10, padx=20, fill="both", expand=True)
        
        frame_cliente = ttk.Frame(notebook)
        notebook.add(frame_cliente, text="Datos del Cliente")
        
        cliente_frame = tk.LabelFrame(frame_cliente, text="INFORMACIÓN DEL CLIENTE", 
                                     font=("Arial", 12, "bold"), fg=self.colores['vino'],
                                     padx=20, pady=20, bg=self.colores['gris_fondo'])
        cliente_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        tk.Label(cliente_frame, text="Nombre del Cliente:", font=("Arial", 11),
                bg=self.colores['gris_fondo'], fg=self.colores['gris_oscuro']).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        nombre_cliente_var = tk.StringVar()
        tk.Entry(cliente_frame, textvariable=nombre_cliente_var, width=30, font=("Arial", 11)).grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(cliente_frame, text="Teléfono:", font=("Arial", 11),
                bg=self.colores['gris_fondo'], fg=self.colores['gris_oscuro']).grid(row=0, column=2, padx=10, pady=10, sticky="w")
        telefono_var = tk.StringVar()
        tk.Entry(cliente_frame, textvariable=telefono_var, width=20, font=("Arial", 11)).grid(row=0, column=3, padx=10, pady=10)
        
        tk.Label(cliente_frame, text="Email:", font=("Arial", 11),
                bg=self.colores['gris_fondo'], fg=self.colores['gris_oscuro']).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        email_var = tk.StringVar()
        tk.Entry(cliente_frame, textvariable=email_var, width=30, font=("Arial", 11)).grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(cliente_frame, text="Dirección:", font=("Arial", 11),
                bg=self.colores['gris_fondo'], fg=self.colores['gris_oscuro']).grid(row=1, column=2, padx=10, pady=10, sticky="w")
        direccion_var = tk.StringVar()
        tk.Entry(cliente_frame, textvariable=direccion_var, width=40, font=("Arial", 11)).grid(row=1, column=3, padx=10, pady=10)
        
        frame_materiales = ttk.Frame(notebook)
        notebook.add(frame_materiales, text="Materiales")
        
        columns = ("Material", "Cantidad", "Precio Unitario", "Precio Total")
        tree_materiales = ttk.Treeview(frame_materiales, columns=columns, show="headings", height=8)
        
        for col in columns:
            tree_materiales.heading(col, text=col)
            if col == "Material":
                tree_materiales.column(col, width=300)
            elif col == "Cantidad":
                tree_materiales.column(col, width=100)
            else:
                tree_materiales.column(col, width=150)
        
        tree_materiales.pack(pady=10, padx=10, fill="both", expand=True)
        
        frame_agregar_mat = tk.Frame(frame_materiales, bg=self.colores['gris_fondo'])
        frame_agregar_mat.pack(pady=10)
        
        tk.Label(frame_agregar_mat, text="Material:", bg=self.colores['gris_fondo'], 
                font=("Arial", 10), fg=self.colores['gris_oscuro']).grid(row=0, column=0, padx=5)
        material_entry = tk.Entry(frame_agregar_mat, width=25, font=("Arial", 10))
        material_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(frame_agregar_mat, text="Cantidad:", bg=self.colores['gris_fondo'], 
                font=("Arial", 10), fg=self.colores['gris_oscuro']).grid(row=0, column=2, padx=5)
        cantidad_mat_entry = tk.Entry(frame_agregar_mat, width=10, font=("Arial", 10))
        cantidad_mat_entry.grid(row=0, column=3, padx=5)
        
        tk.Label(frame_agregar_mat, text="Precio Unitario:", bg=self.colores['gris_fondo'], 
                font=("Arial", 10), fg=self.colores['gris_oscuro']).grid(row=0, column=4, padx=5)
        precio_mat_entry = tk.Entry(frame_agregar_mat, width=15, font=("Arial", 10))
        precio_mat_entry.grid(row=0, column=5, padx=5)
        
        frame_fabricacion = ttk.Frame(notebook)
        notebook.add(frame_fabricacion, text="Fabricación")
        
        costo_materiales_var = tk.StringVar()
        tiempo_elab_var = tk.StringVar()
        mano_obra_diaria_var = tk.StringVar()
        costo_nomina_var = tk.StringVar()
        porcentaje_var = tk.StringVar()
        costo_fabricacion_var = tk.StringVar()
        
        fabricacion_frame = tk.Frame(frame_fabricacion, bg=self.colores['gris_fondo'])
        fabricacion_frame.pack(pady=20)
        
        tk.Label(fabricacion_frame, text="Costo de Materiales:", font=("Arial", 11),
                fg=self.colores['gris_oscuro']).grid(row=0, column=0, padx=10, pady=5)
        tk.Entry(fabricacion_frame, textvariable=costo_materiales_var, state='readonly', 
                width=20, font=("Arial", 11)).grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(fabricacion_frame, text="+30% sobre materiales:", font=("Arial", 11),
                fg=self.colores['vino']).grid(row=1, column=0, padx=10, pady=5)
        porcentaje_materiales_var = tk.StringVar()
        tk.Label(fabricacion_frame, textvariable=porcentaje_materiales_var, font=("Arial", 12, "bold"),
                fg=self.colores['vino']).grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(fabricacion_frame, text="Tiempo de Elaboración (días):", font=("Arial", 11),
                fg=self.colores['gris_oscuro']).grid(row=2, column=0, padx=10, pady=5)
        tiempo_entry = tk.Entry(fabricacion_frame, textvariable=tiempo_elab_var, width=20, font=("Arial", 11))
        tiempo_entry.grid(row=2, column=1, padx=10, pady=5)
        
        tk.Label(fabricacion_frame, text="Mano de Obra Diaria ($):", font=("Arial", 11),
                fg=self.colores['gris_oscuro']).grid(row=3, column=0, padx=10, pady=5)
        mano_obra_frame = tk.Frame(fabricacion_frame, bg=self.colores['gris_fondo'])
        mano_obra_frame.grid(row=3, column=1, padx=10, pady=5)
        mano_obra_opciones = ["80", "85", "90", "95", "100"]
        mano_obra_combo = ttk.Combobox(mano_obra_frame, values=mano_obra_opciones, width=10, font=("Arial", 11))
        mano_obra_combo.set("90")
        mano_obra_combo.pack(side=tk.LEFT)
        tk.Label(mano_obra_frame, text="$/día", font=("Arial", 11),
                bg=self.colores['gris_fondo']).pack(side=tk.LEFT, padx=5)
        
        tk.Label(fabricacion_frame, text="Costo Total de Nómina:", font=("Arial", 11),
                fg=self.colores['gris_oscuro']).grid(row=4, column=0, padx=10, pady=5)
        tk.Entry(fabricacion_frame, textvariable=costo_nomina_var, state='readonly', 
                width=20, font=("Arial", 11)).grid(row=4, column=1, padx=10, pady=5)
        
        tk.Label(fabricacion_frame, text="Porcentaje de Ganancia:", font=("Arial", 11),
                fg=self.colores['gris_oscuro']).grid(row=5, column=0, padx=10, pady=5)
        porcentaje_opciones = ["10%", "15%", "20%", "25%", "30%", "35%", "40%", "45%", "50%"]
        porcentaje_combo = ttk.Combobox(fabricacion_frame, values=porcentaje_opciones, width=15, font=("Arial", 11))
        porcentaje_combo.set("20%")
        porcentaje_combo.grid(row=5, column=1, padx=10, pady=5)
        
        frame_adicionales = ttk.Frame(notebook)
        notebook.add(frame_adicionales, text="Costos Adicionales")
        
        costo_transporte_var = tk.StringVar()
        costo_instalacion_var = tk.StringVar()
        costo_adicional_total_var = tk.StringVar()
        
        adicionales_frame = tk.Frame(frame_adicionales, bg=self.colores['gris_fondo'])
        adicionales_frame.pack(pady=20)
        
        tk.Label(adicionales_frame, text="Costo de Transporte ($):", font=("Arial", 11),
                fg=self.colores['gris_oscuro']).grid(row=0, column=0, padx=10, pady=10)
        tk.Entry(adicionales_frame, textvariable=costo_transporte_var, width=20, font=("Arial", 11)).grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(adicionales_frame, text="Costo de Instalación ($):", font=("Arial", 11),
                fg=self.colores['gris_oscuro']).grid(row=1, column=0, padx=10, pady=10)
        tk.Entry(adicionales_frame, textvariable=costo_instalacion_var, width=20, font=("Arial", 11)).grid(row=1, column=1, padx=10, pady=10)
        
        frame_total_venta = tk.Frame(ventana, bg=self.colores['blanco'], relief=tk.RAISED, bd=2)
        frame_total_venta.pack(pady=15, padx=20, fill="x")
        
        frame_abono = tk.Frame(frame_total_venta, bg=self.colores['blanco'])
        frame_abono.pack(pady=10)
        
        tk.Label(frame_abono, text="Abono del Cliente ($):", font=("Arial", 12), 
                bg=self.colores['blanco'], fg=self.colores['gris_oscuro']).pack(side=tk.LEFT, padx=10)
        abono_var = tk.StringVar(value="0")
        tk.Entry(frame_abono, textvariable=abono_var, width=15, font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
        
        total_general_var = tk.StringVar(value="$0.00")
        saldo_pendiente_var = tk.StringVar(value="$0.00")
        
        tk.Label(frame_total_venta, text="TOTAL DE LA FACTURA:", font=("Arial", 14, "bold"), 
                bg=self.colores['blanco'], fg=self.colores['vino']).pack(pady=5)
        tk.Label(frame_total_venta, textvariable=total_general_var, font=("Arial", 20, "bold"), 
                fg=self.colores['vino'], bg=self.colores['blanco']).pack(pady=5)
        
        tk.Label(frame_total_venta, text="SALDO PENDIENTE:", font=("Arial", 12, "bold"), 
                bg=self.colores['blanco'], fg=self.colores['gris_oscuro']).pack(pady=5)
        tk.Label(frame_total_venta, textvariable=saldo_pendiente_var, font=("Arial", 16, "bold"), 
                fg=self.colores['vino'], bg=self.colores['blanco']).pack(pady=5)
        
        def actualizar_total_venta():
            total_materiales = 0
            for item in tree_materiales.get_children():
                values = tree_materiales.item(item)['values']
                if values and len(values) > 3:
                    subtotal_str = values[3].replace('$', '')
                    total_materiales += float(subtotal_str)
            
            costo_materiales_var.set(f"${total_materiales:.2f}")
            
            porcentaje_30 = total_materiales * 0.30
            porcentaje_materiales_var.set(f"+30%: ${porcentaje_30:.2f}")
            
            try:
                tiempo = float(tiempo_elab_var.get() if tiempo_elab_var.get() else 0)
                mano_obra_diaria = float(mano_obra_combo.get() if mano_obra_combo.get() else 90)
                costo_nomina = mano_obra_diaria * tiempo
                costo_nomina_var.set(f"${costo_nomina:.2f}")
            except:
                costo_nomina = 0
                costo_nomina_var.set("$0.00")
            
            costo_fab = total_materiales + porcentaje_30 + costo_nomina
            
            try:
                porcentaje_str = porcentaje_combo.get()
                if porcentaje_str:
                    porcentaje = float(porcentaje_str.replace('%', '')) / 100
                    ganancia = costo_fab * porcentaje
                else:
                    ganancia = 0
                costo_con_ganancia = costo_fab + ganancia
                costo_fabricacion_var.set(f"${costo_con_ganancia:.2f}")
            except:
                costo_con_ganancia = costo_fab
                costo_fabricacion_var.set(f"${costo_fab:.2f}")
            
            try:
                costo_transporte = float(costo_transporte_var.get() if costo_transporte_var.get() else 0)
                costo_instalacion = float(costo_instalacion_var.get() if costo_instalacion_var.get() else 0)
                costo_adicional_total = costo_transporte + costo_instalacion
                costo_adicional_total_var.set(f"${costo_adicional_total:.2f}")
            except:
                costo_adicional_total = 0
                costo_adicional_total_var.set("$0.00")
            
            total = costo_con_ganancia + costo_adicional_total
            total_general_var.set(f"${total:.2f}")
            
            try:
                abono = float(abono_var.get() if abono_var.get() else 0)
                saldo = total - abono
                saldo_pendiente_var.set(f"${saldo:.2f}")
            except:
                saldo_pendiente_var.set(f"${total:.2f}")
        
        def agregar_material_venta():
            material = material_entry.get()
            cantidad = cantidad_mat_entry.get()
            precio_unitario = precio_mat_entry.get()
            
            if material and cantidad and precio_unitario:
                try:
                    cantidad = float(cantidad)
                    precio_unitario = float(precio_unitario)
                    precio_total = cantidad * precio_unitario
                    tree_materiales.insert("", "end", values=(material, cantidad, f"${precio_unitario:.2f}", f"${precio_total:.2f}"))
                    material_entry.delete(0, tk.END)
                    cantidad_mat_entry.delete(0, tk.END)
                    precio_mat_entry.delete(0, tk.END)
                    actualizar_total_venta()
                except ValueError:
                    messagebox.showerror("Error", "Cantidad y precio deben ser números")
            else:
                messagebox.showwarning("Advertencia", "Complete todos los campos")
        
        btn_agregar_mat = tk.Button(frame_agregar_mat, text="Agregar Material", 
                                   command=agregar_material_venta, 
                                   bg=self.colores['vino'], fg="white", 
                                   font=("Arial", 10, "bold"),
                                   activebackground=self.colores['vino_claro'])
        btn_agregar_mat.grid(row=0, column=6, padx=10)
        
        def calcular_fabricacion():
            actualizar_total_venta()
        
        btn_calcular_fab = tk.Button(fabricacion_frame, text="Calcular Costos", 
                                    command=calcular_fabricacion, 
                                    bg=self.colores['gris_medio'], fg="white", 
                                    font=("Arial", 11, "bold"),
                                    activebackground=self.colores['gris_oscuro'])
        btn_calcular_fab.grid(row=6, column=0, columnspan=2, pady=15)
        
        tk.Label(fabricacion_frame, text="Costo de Fabricación con Ganancia:", font=("Arial", 11, "bold"),
                fg=self.colores['vino']).grid(row=7, column=0, padx=10, pady=5)
        tk.Label(fabricacion_frame, textvariable=costo_fabricacion_var, font=("Arial", 14, "bold"), 
                fg=self.colores['vino_claro']).grid(row=7, column=1, padx=10, pady=5)
        
        def calcular_adicionales():
            actualizar_total_venta()
        
        btn_calcular_adicionales = tk.Button(adicionales_frame, text="Calcular Costos Adicionales", 
                                            command=calcular_adicionales, 
                                            bg=self.colores['gris_medio'], fg="white", 
                                            font=("Arial", 11, "bold"),
                                            activebackground=self.colores['gris_oscuro'])
        btn_calcular_adicionales.grid(row=2, column=0, columnspan=2, pady=15)
        
        tk.Label(adicionales_frame, text="Total Costos Adicionales:", font=("Arial", 11, "bold"),
                fg=self.colores['vino']).grid(row=3, column=0, padx=10, pady=5)
        tk.Label(adicionales_frame, textvariable=costo_adicional_total_var, font=("Arial", 14, "bold"), 
                fg=self.colores['vino_claro']).grid(row=3, column=1, padx=10, pady=5)
        
        if presupuesto_cargado:
            nombre_cliente_var.set(presupuesto_cargado['cliente'])
            telefono_var.set(presupuesto_cargado.get('telefono', ''))
            email_var.set(presupuesto_cargado.get('email', ''))
            
            for material in presupuesto_cargado['materiales']:
                tree_materiales.insert("", "end", values=(
                    material['descripcion'],
                    material['cantidad'],
                    material['precio_unitario'],
                    material['subtotal']
                ))
            
            if presupuesto_cargado.get('tiempo_elaboracion'):
                tiempo_elab_var.set(presupuesto_cargado['tiempo_elaboracion'])
            if presupuesto_cargado.get('mano_obra_diaria'):
                mano_obra_combo.set(presupuesto_cargado['mano_obra_diaria'])
            if presupuesto_cargado.get('porcentaje_ganancia'):
                porcentaje_combo.set(presupuesto_cargado['porcentaje_ganancia'])
            if presupuesto_cargado.get('costo_transporte'):
                costo_transporte_var.set(str(presupuesto_cargado['costo_transporte']))
            if presupuesto_cargado.get('costo_instalacion'):
                costo_instalacion_var.set(str(presupuesto_cargado['costo_instalacion']))
            
            for presupuesto in self.presupuestos:
                if presupuesto['id'] == presupuesto_cargado['id']:
                    presupuesto['estado'] = 'FACTURADO'
                    break
            self.guardar_datos()
            
            actualizar_total_venta()
        
        def generar_factura():
            nombre_cliente = nombre_cliente_var.get()
            if not nombre_cliente:
                messagebox.showwarning("Advertencia", "Ingrese el nombre del cliente")
                return
            
            total = float(total_general_var.get().replace('$', ''))
            if total > 0:
                abono = float(abono_var.get() if abono_var.get() else 0)
                saldo = total - abono
                estado = "FINIQUITADO" if saldo <= 0 else "POR FINIQUITAR"
                
                factura_id = f"F-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                fecha = datetime.now().strftime('%d/%m/%Y %H:%M')
                
                materiales_data = []
                for item in tree_materiales.get_children():
                    values = tree_materiales.item(item)['values']
                    if values:
                        materiales_data.append({
                            'material': values[0],
                            'cantidad': values[1],
                            'precio_unitario': values[2],
                            'precio_total': values[3]
                        })
                
                factura = {
                    'id': factura_id,
                    'cliente': nombre_cliente,
                    'telefono': telefono_var.get(),
                    'email': email_var.get(),
                    'direccion': direccion_var.get(),
                    'fecha': fecha,
                    'total': total,
                    'abono': abono,
                    'saldo': saldo,
                    'estado': estado,
                    'materiales': materiales_data,
                    'costo_fabricacion': costo_fabricacion_var.get(),
                    'costo_transporte': costo_transporte_var.get(),
                    'costo_instalacion': costo_instalacion_var.get(),
                    'tiempo_elaboracion': tiempo_elab_var.get(),
                    'mano_obra_diaria': mano_obra_combo.get(),
                    'porcentaje_ganancia': porcentaje_combo.get()
                }
                
                self.facturas.append(factura)
                self.guardar_datos()
                
                # Guardar TXT en carpeta facturas_txt
                nombre_archivo_txt = f"facturas_txt/factura_{factura_id}.txt"
                total_materiales_calc = sum(float(m['precio_total'].replace('$', '')) for m in materiales_data)
                
                with open(nombre_archivo_txt, 'w', encoding='utf-8') as f:
                    f.write("="*80 + "\n")
                    f.write("FACTURA DE VENTA - MADERAS IGLOMAR\n")
                    f.write("="*80 + "\n\n")
                    f.write(f"Nº FACTURA: {factura_id}\n")
                    f.write(f"FECHA: {fecha}\n")
                    f.write(f"ESTADO: {estado}\n\n")
                    f.write("DATOS DEL CLIENTE:\n")
                    f.write("-"*80 + "\n")
                    f.write(f"Nombre: {nombre_cliente}\n")
                    f.write(f"Teléfono: {telefono_var.get()}\n")
                    f.write(f"Email: {email_var.get()}\n")
                    f.write(f"Dirección: {direccion_var.get()}\n\n")
                    f.write("MATERIALES:\n")
                    f.write("-"*80 + "\n")
                    f.write(f"{'Material':<30} {'Cantidad':<10} {'Precio Unitario':<15} {'Precio Total':<15}\n")
                    f.write("-"*80 + "\n")
                    for item in tree_materiales.get_children():
                        values = tree_materiales.item(item)['values']
                        if values:
                            f.write(f"{values[0]:<30} {values[1]:<10} {values[2]:<15} {values[3]:<15}\n")
                    
                    f.write("\nCOSTOS:\n")
                    f.write("-"*80 + "\n")
                    f.write(f"Total Materiales: ${total_materiales_calc:.2f}\n")
                    f.write(f"+30% sobre materiales: ${total_materiales_calc * 0.30:.2f}\n")
                    f.write(f"Costo de Nómina: {costo_nomina_var.get()}\n")
                    f.write(f"Costo de Fabricación con Ganancia: {costo_fabricacion_var.get()}\n")
                    f.write(f"Costo de Transporte: {costo_transporte_var.get()}\n")
                    f.write(f"Costo de Instalación: {costo_instalacion_var.get()}\n\n")
                    f.write("="*80 + "\n")
                    f.write("RESUMEN DE PAGO:\n")
                    f.write("-"*80 + "\n")
                    f.write(f"TOTAL FACTURA: ${total:.2f}\n")
                    f.write(f"ABONO: ${abono:.2f}\n")
                    f.write(f"SALDO PENDIENTE: ${saldo:.2f}\n")
                    f.write(f"ESTADO: {estado}\n")
                    f.write("="*80 + "\n")
                
                # Generar PDF
                pdf_path = self.generar_pdf_factura(
                    factura, materiales_data, total_materiales_calc,
                    costo_nomina_var.get(), costo_fabricacion_var.get(),
                    costo_transporte_var.get(), costo_instalacion_var.get()
                )
                
                messagebox.showinfo("Éxito", f"Factura generada:\nTXT: {nombre_archivo_txt}\nPDF: {pdf_path}\nEstado: {estado}")
                ventana.destroy()
            else:
                messagebox.showwarning("Advertencia", "No hay datos para generar la factura")
        
        frame_botones = tk.Frame(ventana, bg=self.colores['gris_fondo'])
        frame_botones.pack(pady=15)
        
        btn_actualizar = tk.Button(frame_botones, text="Actualizar Total", command=actualizar_total_venta,
                                  bg=self.colores['gris_medio'], fg="white", font=("Arial", 11, "bold"), width=15,
                                  activebackground=self.colores['gris_oscuro'])
        btn_actualizar.pack(side=tk.LEFT, padx=10)
        
        btn_facturar = tk.Button(frame_botones, text="Generar Factura", command=generar_factura,
                                bg=self.colores['vino'], fg="white", font=("Arial", 11, "bold"), width=15,
                                activebackground=self.colores['vino_claro'])
        btn_facturar.pack(side=tk.LEFT, padx=10)
        
        abono_var.trace('w', lambda *args: actualizar_total_venta())
        tiempo_elab_var.trace('w', lambda *args: actualizar_total_venta())
        mano_obra_combo.bind('<<ComboboxSelected>>', lambda e: actualizar_total_venta())
        porcentaje_combo.bind('<<ComboboxSelected>>', lambda e: actualizar_total_venta())
        costo_transporte_var.trace('w', lambda *args: actualizar_total_venta())
        costo_instalacion_var.trace('w', lambda *args: actualizar_total_venta())
        
        actualizar_total_venta()
    
    def modulo_administracion(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Módulo de Administración - Maderas Iglomar")
        ventana.geometry("1300x800")
        ventana.configure(bg=self.colores['gris_fondo'])
        
        titulo = tk.Label(ventana, text="MÓDULO DE ADMINISTRACIÓN", 
                         font=("Arial", 18, "bold"), bg=self.colores['gris_fondo'], 
                         fg=self.colores['vino'])
        titulo.pack(pady=15)
        
        notebook = ttk.Notebook(ventana)
        notebook.pack(pady=10, padx=20, fill="both", expand=True)
        
        frame_facturas = ttk.Frame(notebook)
        notebook.add(frame_facturas, text="Facturas")
        
        frame_filtros = tk.Frame(frame_facturas, bg=self.colores['gris_fondo'])
        frame_filtros.pack(pady=10, padx=10, fill="x")
        
        tk.Label(frame_filtros, text="Filtrar por estado:", bg=self.colores['gris_fondo'], 
                font=("Arial", 10), fg=self.colores['gris_oscuro']).pack(side=tk.LEFT, padx=5)
        filtro_estado = ttk.Combobox(frame_filtros, values=["TODAS", "POR FINIQUITAR", "FINIQUITADO"], width=15)
        filtro_estado.set("TODAS")
        filtro_estado.pack(side=tk.LEFT, padx=5)
        
        tk.Label(frame_filtros, text="Buscar cliente:", bg=self.colores['gris_fondo'], 
                font=("Arial", 10), fg=self.colores['gris_oscuro']).pack(side=tk.LEFT, padx=5)
        busqueda_entry = tk.Entry(frame_filtros, width=25, font=("Arial", 10))
        busqueda_entry.pack(side=tk.LEFT, padx=5)
        
        columns = ("ID", "Cliente", "Fecha", "Total", "Abono", "Saldo", "Estado")
        tree_facturas = ttk.Treeview(frame_facturas, columns=columns, show="headings", height=12)
        
        for col in columns:
            tree_facturas.heading(col, text=col)
            if col == "ID":
                tree_facturas.column(col, width=150)
            elif col == "Cliente":
                tree_facturas.column(col, width=250)
            elif col == "Fecha":
                tree_facturas.column(col, width=150)
            else:
                tree_facturas.column(col, width=120)
        
        tree_facturas.pack(pady=10, padx=10, fill="both", expand=True)
        
        def cargar_facturas():
            for item in tree_facturas.get_children():
                tree_facturas.delete(item)
            
            filtro = filtro_estado.get()
            busqueda = busqueda_entry.get().lower()
            
            for factura in self.facturas:
                if filtro != "TODAS" and factura['estado'] != filtro:
                    continue
                if busqueda and busqueda not in factura['cliente'].lower():
                    continue
                
                tree_facturas.insert("", "end", values=(
                    factura['id'],
                    factura['cliente'],
                    factura['fecha'],
                    f"${factura['total']:.2f}",
                    f"${factura['abono']:.2f}",
                    f"${factura['saldo']:.2f}",
                    factura['estado']
                ))
        
        frame_acciones = tk.Frame(frame_facturas, bg=self.colores['gris_fondo'])
        frame_acciones.pack(pady=10)
        
        def registrar_abono():
            seleccion = tree_facturas.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Seleccione una factura")
                return
            
            item = tree_facturas.item(seleccion[0])
            factura_id = item['values'][0]
            
            for factura in self.facturas:
                if factura['id'] == factura_id:
                    if factura['estado'] == "FINIQUITADO":
                        messagebox.showinfo("Info", "Esta factura ya está finiquitada")
                        return
                    
                    ventana_abono = tk.Toplevel(ventana)
                    ventana_abono.title("Registrar Abono")
                    ventana_abono.geometry("450x400")
                    ventana_abono.configure(bg=self.colores['gris_fondo'])
                    
                    tk.Label(ventana_abono, text=f"Factura: {factura_id}", 
                            font=("Arial", 14, "bold"), bg=self.colores['gris_fondo'], 
                            fg=self.colores['vino']).pack(pady=15)
                    tk.Label(ventana_abono, text=f"Cliente: {factura['cliente']}", 
                            font=("Arial", 11), bg=self.colores['gris_fondo'], 
                            fg=self.colores['gris_oscuro']).pack()
                    tk.Label(ventana_abono, text=f"Total: ${factura['total']:.2f}", 
                            font=("Arial", 11), bg=self.colores['gris_fondo'], 
                            fg=self.colores['gris_oscuro']).pack()
                    tk.Label(ventana_abono, text=f"Abonado: ${factura['abono']:.2f}", 
                            font=("Arial", 11), bg=self.colores['gris_fondo'], 
                            fg=self.colores['gris_oscuro']).pack()
                    tk.Label(ventana_abono, text=f"Saldo pendiente: ${factura['saldo']:.2f}", 
                            font=("Arial", 12, "bold"), bg=self.colores['gris_fondo'], 
                            fg=self.colores['vino']).pack(pady=10)
                    
                    tk.Label(ventana_abono, text="Monto a abonar:", font=("Arial", 11), 
                            bg=self.colores['gris_fondo'], fg=self.colores['gris_oscuro']).pack(pady=10)
                    monto_var = tk.StringVar()
                    tk.Entry(ventana_abono, textvariable=monto_var, width=20, font=("Arial", 11)).pack()
                    
                    def procesar_abono():
                        try:
                            monto = float(monto_var.get())
                            if monto <= 0:
                                messagebox.showwarning("Advertencia", "Ingrese un monto válido")
                                return
                            
                            if monto > factura['saldo']:
                                messagebox.showwarning("Advertencia", f"El abono no puede ser mayor al saldo pendiente (${factura['saldo']:.2f})")
                                return
                            
                            factura['abono'] += monto
                            factura['saldo'] -= monto
                            
                            if factura['saldo'] <= 0:
                                factura['estado'] = "FINIQUITADO"
                                factura['saldo'] = 0
                            
                            self.guardar_datos()
                            cargar_facturas()
                            actualizar_estadisticas_semanales()
                            messagebox.showinfo("Éxito", f"Abono de ${monto:.2f} registrado")
                            ventana_abono.destroy()
                        except ValueError:
                            messagebox.showerror("Error", "Ingrese un monto válido")
                    
                    tk.Button(ventana_abono, text="Registrar Abono", command=procesar_abono,
                             bg=self.colores['vino'], fg="white", font=("Arial", 11, "bold"), 
                             width=20, activebackground=self.colores['vino_claro']).pack(pady=15)
                    break
        
        tk.Button(frame_acciones, text="Registrar Abono", command=registrar_abono,
                 bg=self.colores['vino_claro'], fg="white", font=("Arial", 10, "bold"), width=15,
                 activebackground=self.colores['vino']).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_acciones, text="Actualizar", command=cargar_facturas,
                 bg=self.colores['gris_medio'], fg="white", font=("Arial", 10, "bold"), width=15,
                 activebackground=self.colores['gris_oscuro']).pack(side=tk.LEFT, padx=5)
        
        filtro_estado.bind('<<ComboboxSelected>>', lambda e: cargar_facturas())
        busqueda_entry.bind('<KeyRelease>', lambda e: cargar_facturas())
        
        frame_gastos = ttk.Frame(notebook)
        notebook.add(frame_gastos, text="Gastos y Proveedores")
        
        frame_agregar_gasto = tk.LabelFrame(frame_gastos, text="Agregar Gasto", 
                                           font=("Arial", 12, "bold"), fg=self.colores['vino'],
                                           padx=15, pady=15, bg=self.colores['gris_fondo'])
        frame_agregar_gasto.pack(pady=10, padx=10, fill="x")
        
        tk.Label(frame_agregar_gasto, text="Descripción:", font=("Arial", 10),
                bg=self.colores['gris_fondo'], fg=self.colores['gris_oscuro']).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        gasto_desc_var = tk.StringVar()
        tk.Entry(frame_agregar_gasto, textvariable=gasto_desc_var, width=30, font=("Arial", 10)).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(frame_agregar_gasto, text="Monto ($):", font=("Arial", 10),
                bg=self.colores['gris_fondo'], fg=self.colores['gris_oscuro']).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        gasto_monto_var = tk.StringVar()
        tk.Entry(frame_agregar_gasto, textvariable=gasto_monto_var, width=15, font=("Arial", 10)).grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(frame_agregar_gasto, text="Categoría:", font=("Arial", 10),
                bg=self.colores['gris_fondo'], fg=self.colores['gris_oscuro']).grid(row=0, column=4, padx=5, pady=5, sticky="w")
        categorias = ["Materiales", "Nómina", "Alquiler", "Servicios", "Transporte", "Proveedores", "Otros"]
        gasto_categoria_combo = ttk.Combobox(frame_agregar_gasto, values=categorias, width=15)
        gasto_categoria_combo.grid(row=0, column=5, padx=5, pady=5)
        
        frame_proveedor = tk.Frame(frame_agregar_gasto, bg=self.colores['gris_fondo'])
        frame_proveedor.grid(row=1, column=0, columnspan=6, pady=5)
        
        tk.Label(frame_proveedor, text="Proveedor:", font=("Arial", 10), 
                bg=self.colores['gris_fondo'], fg=self.colores['gris_oscuro']).pack(side=tk.LEFT, padx=5)
        proveedor_combo = ttk.Combobox(frame_proveedor, values=[p['nombre'] for p in self.proveedores], width=25)
        proveedor_combo.pack(side=tk.LEFT, padx=5)
        
        tk.Label(frame_proveedor, text="¿Es deuda?", font=("Arial", 10), 
                bg=self.colores['gris_fondo'], fg=self.colores['gris_oscuro']).pack(side=tk.LEFT, padx=5)
        es_deuda_var = tk.BooleanVar()
        tk.Checkbutton(frame_proveedor, variable=es_deuda_var, bg=self.colores['gris_fondo']).pack(side=tk.LEFT, padx=5)
        
        def actualizar_visibilidad_proveedor(*args):
            if gasto_categoria_combo.get() == "Proveedores":
                frame_proveedor.pack()
            else:
                frame_proveedor.pack_forget()
        
        gasto_categoria_combo.bind('<<ComboboxSelected>>', actualizar_visibilidad_proveedor)
        
        def agregar_gasto():
            descripcion = gasto_desc_var.get()
            monto = gasto_monto_var.get()
            categoria = gasto_categoria_combo.get()
            
            if descripcion and monto and categoria:
                try:
                    monto = float(monto)
                    gasto = {
                        'id': f"G-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        'descripcion': descripcion,
                        'monto': monto,
                        'categoria': categoria,
                        'fecha': datetime.now().strftime('%d/%m/%Y %H:%M'),
                        'proveedor': proveedor_combo.get() if categoria == "Proveedores" else None,
                        'es_deuda': es_deuda_var.get() if categoria == "Proveedores" else False
                    }
                    self.gastos.append(gasto)
                    
                    if categoria == "Proveedores" and es_deuda_var.get():
                        for proveedor in self.proveedores:
                            if proveedor['nombre'] == proveedor_combo.get():
                                proveedor['deuda'] += monto
                                break
                    
                    self.guardar_datos()
                    cargar_gastos()
                    actualizar_estadisticas_semanales()
                    gasto_desc_var.set("")
                    gasto_monto_var.set("")
                    gasto_categoria_combo.set("")
                    proveedor_combo.set("")
                    es_deuda_var.set(False)
                    messagebox.showinfo("Éxito", "Gasto registrado")
                except ValueError:
                    messagebox.showerror("Error", "Ingrese un monto válido")
            else:
                messagebox.showwarning("Advertencia", "Complete todos los campos")
        
        tk.Button(frame_agregar_gasto, text="Agregar Gasto", command=agregar_gasto,
                 bg=self.colores['vino'], fg="white", font=("Arial", 10, "bold"), width=15,
                 activebackground=self.colores['vino_claro']).grid(row=0, column=6, padx=10)
        
        columns_gastos = ("ID", "Fecha", "Descripción", "Categoría", "Proveedor", "Monto")
        tree_gastos = ttk.Treeview(frame_gastos, columns=columns_gastos, show="headings", height=8)
        
        for col in columns_gastos:
            tree_gastos.heading(col, text=col)
            if col == "ID":
                tree_gastos.column(col, width=120)
            elif col == "Descripción":
                tree_gastos.column(col, width=250)
            elif col == "Categoría":
                tree_gastos.column(col, width=120)
            elif col == "Proveedor":
                tree_gastos.column(col, width=150)
            else:
                tree_gastos.column(col, width=120)
        
        tree_gastos.pack(pady=10, padx=10, fill="both", expand=True)
        
        def cargar_gastos():
            for item in tree_gastos.get_children():
                tree_gastos.delete(item)
            
            for gasto in self.gastos:
                tree_gastos.insert("", "end", values=(
                    gasto['id'],
                    gasto['fecha'],
                    gasto['descripcion'],
                    gasto['categoria'],
                    gasto.get('proveedor', '-'),
                    f"${gasto['monto']:.2f}"
                ))
        
        frame_proveedores = tk.LabelFrame(frame_gastos, text="Gestión de Proveedores", 
                                         font=("Arial", 12, "bold"), fg=self.colores['vino'],
                                         padx=15, pady=15, bg=self.colores['gris_fondo'])
        frame_proveedores.pack(pady=10, padx=10, fill="x")
        
        frame_nuevo_proveedor = tk.Frame(frame_proveedores, bg=self.colores['gris_fondo'])
        frame_nuevo_proveedor.pack(pady=5)
        
        tk.Label(frame_nuevo_proveedor, text="Nuevo Proveedor:", font=("Arial", 10),
                bg=self.colores['gris_fondo'], fg=self.colores['gris_oscuro']).pack(side=tk.LEFT, padx=5)
        nuevo_proveedor_var = tk.StringVar()
        tk.Entry(frame_nuevo_proveedor, textvariable=nuevo_proveedor_var, width=25, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        def agregar_proveedor():
            nombre = nuevo_proveedor_var.get()
            if nombre:
                proveedor = {
                    'nombre': nombre,
                    'deuda': 0,
                    'fecha_registro': datetime.now().strftime('%d/%m/%Y'),
                    'estado_deuda': 'SIN DEUDA'
                }
                self.proveedores.append(proveedor)
                self.guardar_datos()
                actualizar_lista_proveedores()
                nuevo_proveedor_var.set("")
                messagebox.showinfo("Éxito", "Proveedor agregado")
            else:
                messagebox.showwarning("Advertencia", "Ingrese el nombre del proveedor")
        
        tk.Button(frame_nuevo_proveedor, text="Agregar Proveedor", command=agregar_proveedor,
                 bg=self.colores['vino_claro'], fg="white", font=("Arial", 9, "bold"),
                 activebackground=self.colores['vino']).pack(side=tk.LEFT, padx=5)
        
        columns_proveedores = ("Nombre", "Deuda", "Estado", "Fecha Registro")
        tree_proveedores = ttk.Treeview(frame_proveedores, columns=columns_proveedores, show="headings", height=4)
        
        for col in columns_proveedores:
            tree_proveedores.heading(col, text=col)
            if col == "Nombre":
                tree_proveedores.column(col, width=180)
            elif col == "Deuda":
                tree_proveedores.column(col, width=120)
            elif col == "Estado":
                tree_proveedores.column(col, width=100)
            else:
                tree_proveedores.column(col, width=120)
        
        tree_proveedores.pack(pady=10, fill="x")
        
        def actualizar_lista_proveedores():
            for item in tree_proveedores.get_children():
                tree_proveedores.delete(item)
            
            for proveedor in self.proveedores:
                estado = "FINIQUITADO" if proveedor['deuda'] <= 0 else f"DEBE: ${proveedor['deuda']:.2f}"
                tree_proveedores.insert("", "end", values=(
                    proveedor['nombre'],
                    f"${proveedor['deuda']:.2f}",
                    estado,
                    proveedor['fecha_registro']
                ))
            
            proveedor_combo['values'] = [p['nombre'] for p in self.proveedores]
        
        def abonar_proveedor():
            seleccion = tree_proveedores.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Seleccione un proveedor")
                return
            
            item = tree_proveedores.item(seleccion[0])
            nombre_proveedor = item['values'][0]
            
            for proveedor in self.proveedores:
                if proveedor['nombre'] == nombre_proveedor:
                    if proveedor['deuda'] <= 0:
                        messagebox.showinfo("Info", "Este proveedor no tiene deuda pendiente")
                        return
                    
                    ventana_abono = tk.Toplevel(ventana)
                    ventana_abono.title(f"Abonar a {nombre_proveedor}")
                    ventana_abono.geometry("400x350")
                    ventana_abono.configure(bg=self.colores['gris_fondo'])
                    
                    tk.Label(ventana_abono, text=f"Proveedor: {nombre_proveedor}", 
                            font=("Arial", 12, "bold"), bg=self.colores['gris_fondo'], 
                            fg=self.colores['vino']).pack(pady=15)
                    tk.Label(ventana_abono, text=f"Deuda actual: ${proveedor['deuda']:.2f}", 
                            font=("Arial", 11), bg=self.colores['gris_fondo'], 
                            fg=self.colores['vino_claro']).pack(pady=10)
                    
                    tk.Label(ventana_abono, text="Monto a abonar:", font=("Arial", 11), 
                            bg=self.colores['gris_fondo'], fg=self.colores['gris_oscuro']).pack(pady=10)
                    monto_var = tk.StringVar()
                    tk.Entry(ventana_abono, textvariable=monto_var, width=20, font=("Arial", 11)).pack()
                    
                    def procesar_abono_proveedor():
                        try:
                            monto = float(monto_var.get())
                            if monto <= 0:
                                messagebox.showwarning("Advertencia", "Ingrese un monto válido")
                                return
                            
                            if monto > proveedor['deuda']:
                                messagebox.showwarning("Advertencia", f"El abono no puede ser mayor a la deuda (${proveedor['deuda']:.2f})")
                                return
                            
                            gasto = {
                                'id': f"G-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                                'descripcion': f"Abono a proveedor {nombre_proveedor}",
                                'monto': monto,
                                'categoria': "Proveedores",
                                'fecha': datetime.now().strftime('%d/%m/%Y %H:%M'),
                                'proveedor': nombre_proveedor,
                                'es_deuda': False
                            }
                            self.gastos.append(gasto)
                            
                            proveedor['deuda'] -= monto
                            
                            self.guardar_datos()
                            cargar_gastos()
                            actualizar_lista_proveedores()
                            actualizar_estadisticas_semanales()
                            
                            if proveedor['deuda'] <= 0:
                                messagebox.showinfo("Éxito", f"¡Deuda FINIQUITADA! Abono de ${monto:.2f} registrado")
                            else:
                                messagebox.showinfo("Éxito", f"Abono de ${monto:.2f} registrado. Saldo pendiente: ${proveedor['deuda']:.2f}")
                            
                            ventana_abono.destroy()
                        except ValueError:
                            messagebox.showerror("Error", "Ingrese un monto válido")
                    
                    tk.Button(ventana_abono, text="Registrar Abono", command=procesar_abono_proveedor,
                             bg=self.colores['vino'], fg="white", font=("Arial", 11, "bold"), 
                             width=20, activebackground=self.colores['vino_claro']).pack(pady=15)
                    break
        
        frame_acciones_proveedores = tk.Frame(frame_proveedores, bg=self.colores['gris_fondo'])
        frame_acciones_proveedores.pack(pady=5)
        
        tk.Button(frame_acciones_proveedores, text="Abonar a Proveedor", command=abonar_proveedor,
                 bg=self.colores['vino_claro'], fg="white", font=("Arial", 9, "bold"), width=15,
                 activebackground=self.colores['vino']).pack(side=tk.LEFT, padx=5)
        
        def eliminar_gasto():
            seleccion = tree_gastos.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Seleccione un gasto")
                return
            
            if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este gasto?"):
                item = tree_gastos.item(seleccion[0])
                gasto_id = item['values'][0]
                
                for i, gasto in enumerate(self.gastos):
                    if gasto['id'] == gasto_id:
                        if gasto.get('categoria') == "Proveedores" and gasto.get('es_deuda'):
                            for proveedor in self.proveedores:
                                if proveedor['nombre'] == gasto.get('proveedor'):
                                    proveedor['deuda'] -= gasto['monto']
                                    break
                        del self.gastos[i]
                        break
                
                self.guardar_datos()
                cargar_gastos()
                actualizar_lista_proveedores()
                actualizar_estadisticas_semanales()
                messagebox.showinfo("Éxito", "Gasto eliminado")
        
        frame_acciones_gastos = tk.Frame(frame_gastos, bg=self.colores['gris_fondo'])
        frame_acciones_gastos.pack(pady=10)
        
        tk.Button(frame_acciones_gastos, text="Eliminar Gasto", command=eliminar_gasto,
                 bg=self.colores['gris_medio'], fg="white", font=("Arial", 10, "bold"), width=15,
                 activebackground=self.colores['gris_oscuro']).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_acciones_gastos, text="Actualizar", command=lambda: [cargar_gastos(), actualizar_lista_proveedores()],
                 bg=self.colores['gris_medio'], fg="white", font=("Arial", 10, "bold"), width=15,
                 activebackground=self.colores['gris_oscuro']).pack(side=tk.LEFT, padx=5)
        
        frame_estadisticas = ttk.Frame(notebook)
        notebook.add(frame_estadisticas, text="Estadísticas Financieras")
        
        frame_stats = tk.Frame(frame_estadisticas, bg=self.colores['blanco'], relief=tk.RAISED, bd=2)
        frame_stats.pack(pady=20, padx=20, fill="both", expand=True)
        
        frame_periodo = tk.Frame(frame_stats, bg=self.colores['blanco'])
        frame_periodo.pack(pady=10)
        
        tk.Label(frame_periodo, text="Período:", font=("Arial", 11, "bold"), 
                bg=self.colores['blanco'], fg=self.colores['vino']).pack(side=tk.LEFT, padx=10)
        
        periodo_var = tk.StringVar(value="7")
        
        def cambiar_periodo():
            actualizar_estadisticas_semanales()
        
        tk.Radiobutton(frame_periodo, text="Última semana", variable=periodo_var, 
                      value="7", command=cambiar_periodo, bg=self.colores['blanco'],
                      fg=self.colores['gris_oscuro']).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(frame_periodo, text="Último mes", variable=periodo_var, 
                      value="30", command=cambiar_periodo, bg=self.colores['blanco'],
                      fg=self.colores['gris_oscuro']).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(frame_periodo, text="Todo el histórico", variable=periodo_var, 
                      value="0", command=cambiar_periodo, bg=self.colores['blanco'],
                      fg=self.colores['gris_oscuro']).pack(side=tk.LEFT, padx=5)
        
        stats_frame = tk.Frame(frame_stats, bg=self.colores['blanco'])
        stats_frame.pack(pady=10)
        
        total_ingresos_label = tk.Label(stats_frame, text="Ingresos: $0.00", 
                                       font=("Arial", 13), bg=self.colores['blanco'], 
                                       fg=self.colores['vino'])
        total_ingresos_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        total_gastos_label = tk.Label(stats_frame, text="Gastos: $0.00", 
                                     font=("Arial", 13), bg=self.colores['blanco'], 
                                     fg=self.colores['vino_claro'])
        total_gastos_label.grid(row=0, column=1, padx=20, pady=10, sticky="w")
        
        ganancia_bruta_label = tk.Label(stats_frame, text="Ganancia Bruta: $0.00", 
                                       font=("Arial", 13), bg=self.colores['blanco'], 
                                       fg=self.colores['gris_oscuro'])
        ganancia_bruta_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        capital_obtenido_label = tk.Label(stats_frame, text="Capital Obtenido Neto: $0.00", 
                                         font=("Arial", 14, "bold"), bg=self.colores['blanco'], 
                                         fg=self.colores['vino'])
        capital_obtenido_label.grid(row=2, column=0, columnspan=2, padx=20, pady=15, sticky="w")
        
        deuda_proveedores_label = tk.Label(stats_frame, text="Deuda Total Proveedores: $0.00", 
                                          font=("Arial", 13), bg=self.colores['blanco'], 
                                          fg=self.colores['vino_claro'])
        deuda_proveedores_label.grid(row=3, column=0, columnspan=2, padx=20, pady=10, sticky="w")
        
        separador = tk.Frame(frame_stats, bg=self.colores['gris_claro'], height=2)
        separador.pack(fill="x", padx=20, pady=10)
        
        tk.Label(frame_stats, text="ESTADO DE FACTURAS", font=("Arial", 13, "bold"), 
                bg=self.colores['blanco'], fg=self.colores['vino']).pack(pady=10)
        
        estado_frame = tk.Frame(frame_stats, bg=self.colores['blanco'])
        estado_frame.pack(pady=10)
        
        por_finiquitar_label = tk.Label(estado_frame, text="Por Finiquitar: 0", 
                                       font=("Arial", 11), bg=self.colores['blanco'], 
                                       fg=self.colores['vino_claro'])
        por_finiquitar_label.grid(row=0, column=0, padx=20, pady=5)
        
        finiquitadas_label = tk.Label(estado_frame, text="Finiquitadas: 0", 
                                     font=("Arial", 11), bg=self.colores['blanco'], 
                                     fg=self.colores['vino'])
        finiquitadas_label.grid(row=0, column=1, padx=20, pady=5)
        
        btn_actualizar_stats = tk.Button(frame_stats, text="🔄 Actualizar Estadísticas", 
                                         command=lambda: actualizar_estadisticas_semanales(),
                                         bg=self.colores['vino'], fg="white", 
                                         font=("Arial", 10, "bold"),
                                         height=1, width=20,
                                         activebackground=self.colores['vino_claro'])
        btn_actualizar_stats.pack(pady=15)
        
        def actualizar_estadisticas_semanales():
            try:
                dias = int(periodo_var.get())
                
                if dias == 0:
                    facturas_filtradas = self.facturas.copy()
                    gastos_filtrados = self.gastos.copy()
                    texto_periodo = "Total histórico"
                else:
                    fecha_limite = datetime.now() - timedelta(days=dias)
                    facturas_filtradas = []
                    for factura in self.facturas:
                        try:
                            fecha_factura = datetime.strptime(factura['fecha'].split()[0], '%d/%m/%Y')
                            if fecha_factura >= fecha_limite:
                                facturas_filtradas.append(factura)
                        except:
                            facturas_filtradas.append(factura)
                    
                    gastos_filtrados = []
                    for gasto in self.gastos:
                        try:
                            fecha_gasto = datetime.strptime(gasto['fecha'].split()[0], '%d/%m/%Y')
                            if fecha_gasto >= fecha_limite:
                                gastos_filtrados.append(gasto)
                        except:
                            gastos_filtrados.append(gasto)
                    texto_periodo = f"Últimos {dias} días"
                
                total_ingresos = sum(factura.get('total', 0) for factura in facturas_filtradas)
                total_gastos = sum(gasto.get('monto', 0) for gasto in gastos_filtrados)
                ganancia_bruta = total_ingresos - total_gastos
                total_abonos = sum(factura.get('abono', 0) for factura in facturas_filtradas)
                capital_obtenido = total_abonos - total_gastos
                
                deuda_total = sum(proveedor.get('deuda', 0) for proveedor in self.proveedores)
                
                por_finiquitar = sum(1 for f in facturas_filtradas if f.get('estado') == "POR FINIQUITAR")
                finiquitadas = sum(1 for f in facturas_filtradas if f.get('estado') == "FINIQUITADO")
                
                total_ingresos_label.config(text=f"Ingresos ({texto_periodo}): ${total_ingresos:,.2f}")
                total_gastos_label.config(text=f"Gastos ({texto_periodo}): ${total_gastos:,.2f}")
                ganancia_bruta_label.config(text=f"Ganancia Bruta ({texto_periodo}): ${ganancia_bruta:,.2f}")
                capital_obtenido_label.config(text=f"Capital Obtenido Neto ({texto_periodo}): ${capital_obtenido:,.2f}")
                deuda_proveedores_label.config(text=f"Deuda Total Proveedores: ${deuda_total:,.2f}")
                por_finiquitar_label.config(text=f"Por Finiquitar ({texto_periodo}): {por_finiquitar}")
                finiquitadas_label.config(text=f"Finiquitadas ({texto_periodo}): {finiquitadas}")
                
                if ganancia_bruta >= 0:
                    ganancia_bruta_label.config(fg=self.colores['vino'])
                else:
                    ganancia_bruta_label.config(fg=self.colores['vino_claro'])
                    
            except Exception as e:
                print(f"Error al actualizar estadísticas: {e}")
                messagebox.showerror("Error", f"Error al actualizar estadísticas: {str(e)}")
        
        cargar_facturas()
        cargar_gastos()
        actualizar_lista_proveedores()
        actualizar_estadisticas_semanales()
    
    def modulo_reportes(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Reportes - Maderas Iglomar")
        ventana.geometry("600x400")
        ventana.configure(bg=self.colores['gris_fondo'])
        
        titulo = tk.Label(ventana, text="GENERAR REPORTES", 
                         font=("Arial", 18, "bold"), bg=self.colores['gris_fondo'], 
                         fg=self.colores['vino'])
        titulo.pack(pady=20)
        
        frame_reportes = tk.Frame(ventana, bg=self.colores['gris_fondo'])
        frame_reportes.pack(expand=True, fill="both", padx=40, pady=40)
        
        def generar_reporte_ventas():
            if not self.facturas:
                messagebox.showinfo("Info", "No hay facturas registradas")
                return
            
            nombre_archivo = f"reportes/reporte_ventas_{datetime.now().strftime('%Y%m%d')}.txt"
            
            with open(nombre_archivo, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write("REPORTE DE VENTAS - MADERAS IGLOMAR\n")
                f.write(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
                f.write("="*80 + "\n\n")
                
                total_ventas = 0
                total_abonos = 0
                
                for factura in self.facturas:
                    f.write(f"Factura: {factura['id']}\n")
                    f.write(f"Cliente: {factura['cliente']}\n")
                    f.write(f"Fecha: {factura['fecha']}\n")
                    f.write(f"Total: ${factura['total']:.2f}\n")
                    f.write(f"Abonado: ${factura['abono']:.2f}\n")
                    f.write(f"Saldo: ${factura['saldo']:.2f}\n")
                    f.write(f"Estado: {factura['estado']}\n")
                    f.write("-"*80 + "\n")
                    
                    total_ventas += factura['total']
                    total_abonos += factura['abono']
                
                f.write("\n" + "="*80 + "\n")
                f.write("RESUMEN:\n")
                f.write(f"Total en Ventas: ${total_ventas:.2f}\n")
                f.write(f"Total Abonado: ${total_abonos:.2f}\n")
                f.write(f"Saldo Pendiente Total: ${total_ventas - total_abonos:.2f}\n")
                f.write("="*80 + "\n")
            
            messagebox.showinfo("Éxito", f"Reporte generado: {nombre_archivo}")
        
        def generar_reporte_gastos():
            if not self.gastos:
                messagebox.showinfo("Info", "No hay gastos registrados")
                return
            
            nombre_archivo = f"reportes/reporte_gastos_{datetime.now().strftime('%Y%m%d')}.txt"
            
            with open(nombre_archivo, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write("REPORTE DE GASTOS - MADERAS IGLOMAR\n")
                f.write(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
                f.write("="*80 + "\n\n")
                
                gastos_por_categoria = {}
                total_gastos = 0
                
                for gasto in self.gastos:
                    categoria = gasto['categoria']
                    if categoria not in gastos_por_categoria:
                        gastos_por_categoria[categoria] = 0
                    gastos_por_categoria[categoria] += gasto['monto']
                    total_gastos += gasto['monto']
                    
                    f.write(f"ID: {gasto['id']}\n")
                    f.write(f"Fecha: {gasto['fecha']}\n")
                    f.write(f"Descripción: {gasto['descripcion']}\n")
                    f.write(f"Categoría: {categoria}\n")
                    f.write(f"Monto: ${gasto['monto']:.2f}\n")
                    if gasto.get('proveedor'):
                        f.write(f"Proveedor: {gasto['proveedor']}\n")
                    f.write("-"*80 + "\n")
                
                f.write("\n" + "="*80 + "\n")
                f.write("RESUMEN POR CATEGORÍA:\n")
                for categoria, monto in gastos_por_categoria.items():
                    f.write(f"{categoria}: ${monto:.2f}\n")
                f.write(f"\nTOTAL GASTOS: ${total_gastos:.2f}\n")
                f.write("="*80 + "\n")
            
            messagebox.showinfo("Éxito", f"Reporte generado: {nombre_archivo}")
        
        def generar_reporte_proveedores():
            if not self.proveedores:
                messagebox.showinfo("Info", "No hay proveedores registrados")
                return
            
            nombre_archivo = f"reportes/reporte_proveedores_{datetime.now().strftime('%Y%m%d')}.txt"
            
            with open(nombre_archivo, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write("REPORTE DE PROVEEDORES - MADERAS IGLOMAR\n")
                f.write(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
                f.write("="*80 + "\n\n")
                
                total_deuda = 0
                for proveedor in self.proveedores:
                    f.write(f"Proveedor: {proveedor['nombre']}\n")
                    f.write(f"Deuda: ${proveedor['deuda']:.2f}\n")
                    f.write(f"Estado: {'FINIQUITADO' if proveedor['deuda'] <= 0 else f'DEBE ${proveedor['deuda']:.2f}'}\n")
                    f.write(f"Fecha Registro: {proveedor['fecha_registro']}\n")
                    f.write("-"*80 + "\n")
                    total_deuda += proveedor['deuda']
                
                f.write("\n" + "="*80 + "\n")
                f.write(f"TOTAL DEUDA CON PROVEEDORES: ${total_deuda:.2f}\n")
                f.write("="*80 + "\n")
            
            messagebox.showinfo("Éxito", f"Reporte generado: {nombre_archivo}")
        
        botones = [
            ("📊 Reporte de Ventas", generar_reporte_ventas, self.colores['vino']),
            ("💰 Reporte de Gastos", generar_reporte_gastos, self.colores['vino_claro']),
            ("🏢 Reporte de Proveedores", generar_reporte_proveedores, self.colores['gris_medio']),
            ("📈 Reporte Financiero Completo", None, self.colores['gris_oscuro'])
        ]
        
        for i, (text, command, color) in enumerate(botones):
            btn = tk.Button(frame_reportes, text=text, command=command if command else lambda: messagebox.showinfo("Info", "Próximamente disponible"),
                           bg=color, fg="white", font=("Arial", 11, "bold"),
                           height=2, width=30, relief="raised", bd=2,
                           activebackground=self.colores['vino_claro'] if color != self.colores['gris_oscuro'] else self.colores['gris_medio'])
            btn.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = MiApp(root)
    root.mainloop()