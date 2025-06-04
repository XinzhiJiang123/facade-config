# import viktor as vkt
# import pandas as pd
# import plotly.graph_objects as go
#
#
#
#
# class Parametrization(vkt.Parametrization):
#     _rp_table_default = [
#         {"proj_name": "proj 1", "function": "Modelleur"},
#         {"proj_name": "proj 1"},
#     ]
#     resource_table = vkt.Table("Resource Planning", default=_rp_table_default)
#     resource_table.proj_name = vkt.TextField("Project Name")
#     resource_table.function = vkt.TextField("Function")
#     resource_table.employee_name = vkt.TextField("Employee Name")
#     resource_table.wk1 = vkt.NumberField("Week 1", default=0, num_decimals=1)
#     resource_table.wk2 = vkt.NumberField("Week 2", default=0, num_decimals=1)
#     resource_table.wk3 = vkt.NumberField("Week 3", default=0, num_decimals=1)
#     resource_table.wk4 = vkt.NumberField("Week 4", default=0, num_decimals=1)
#     resource_table.wk5 = vkt.NumberField("Week 5", default=0, num_decimals=1)
#     resource_table.wk6 = vkt.NumberField("Week 6", default=0, num_decimals=1)
#     resource_table.wk7 = vkt.NumberField("Week 7", default=0, num_decimals=1)
#     resource_table.wk8 = vkt.NumberField("Week 8", default=0, num_decimals=1)
#     resource_table.wk9 = vkt.NumberField("Week 9", default=0, num_decimals=1)
#     resource_table.wk10 = vkt.NumberField("Week 10", default=0, num_decimals=1)
#     # robertson = vkt.Table(
#     #     "Robertson table",
#     #     default=_DEFAULT_ROBERTSON_TABLE,
#     #     # visible=vkt.And(
#     #     #     vkt.Lookup("classification.change_table"),
#     #     #     vkt.IsEqual(vkt.Lookup("classification.method"), "robertson"),
#     #     # ),
#     # )
#
#
# class Controller(vkt.Controller):
#     label = "Resource Planning"
#     parametrization = Parametrization
#
#     @vkt.WebView("Resource Planning Table", duration_guess=1)
#     def show_resource_table(self, params, **kwargs):
#         df = pd.DataFrame(params.resource_table)
#         html = df.to_html(classes='table table-striped', index=False)
#         return vkt.WebResult(html=html)
#
#     @vkt.PlotlyView("Resource Allocation Chart", duration_guess=3)
#     def show_resource_chart(self, params, **kwargs):
#         df = pd.DataFrame(params.resource_table)
#
#         fig = go.Figure()
#         for _, row in df.iterrows():
#             weeks = [f"wk{i}" for i in range(1, 11)]
#             fig.add_trace(go.Bar(
#                 name=f"{row['employee_name']} - {row['proj_name']}",
#                 x=weeks,
#                 y=[row[week] for week in weeks],
#                 text=[f"{row[week]:.1f}" for week in weeks],
#                 textposition='auto',
#             ))
#
#         fig.update_layout(
#             title="Resource Allocation per Week",
#             xaxis_title="Week",
#             yaxis_title="Hours",
#             barmode='stack'
#         )
#
#         return vkt.PlotlyResult(fig.to_json())


import viktor as vkt
from viktor.views import DataView, DataResult, PlotlyView, PlotlyResult
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from itertools import product


class Parametrization(vkt.Parametrization):
    facade_size = vkt.Page("1. Facade size")
    facade_size.dimensions = vkt.Section("Dimensions")
    facade_size.dimensions.width = vkt.NumberField("Facade width", min=1, default=10, suffix='m')
    facade_size.dimensions.num_storeys = vkt.IntegerField("Number of storeys", min=1, default=5)
    facade_size.dimensions.storey_height = vkt.NumberField("Height per storey", min=2, default=3, suffix='m')

    facade_size.data = vkt.Section("Data", initially_expanded=False)
    # user-modifiable table for MKI data
    _mki_table_default = [
        {"category": "Facade - open", "material": "Double glazing", "mki_per_unit": 50, "unit": "m² open", "nmd_code": "#nmd_00000"},
        {"category": "Facade - closed", "material": "Prefab concrete sandwich panels", "mki_per_unit": 10, "unit": "m² closed", "nmd_code": "#nmd_00000"},
        {"category": "Facade - closed", "material": "Steel sandwich panels", "mki_per_unit": 11, "unit": "m² closed", "nmd_code": "#nmd_00000"},
        {"category": "Facade - closed", "material": "Timber frame construction (HSB)", "mki_per_unit": 5, "unit": "m² closed", "nmd_code": "#nmd_00000"}
    ]
    _mki_table_category_options = ["Facade - open", "Facade - closed"]
    facade_size.data.mki_subtitle = vkt.Text("MKI data")
    facade_size.data.mki_table = vkt.Table("MKI Table", default=_mki_table_default)
    facade_size.data.mki_table.category = vkt.OptionField("Category", options=_mki_table_category_options)
    facade_size.data.mki_table.material = vkt.TextField("Material")
    facade_size.data.mki_table.mki_per_unit = vkt.NumberField("MKI [€/unit]")
    facade_size.data.mki_table.unit = vkt.TextField("Unit")
    facade_size.data.mki_table.nmd_code = vkt.TextField("NMD code")

    # user-modifiable table for initial cost data
    _cost_table_default = [
        {"category": "Facade - open", "material": "Double glazing", "cost_per_unit": 10, "unit": "m² open"},
        {"category": "Facade - closed", "material": "Prefab concrete sandwich panels", "cost_per_unit": 5, "unit": "m² closed"},
        {"category": "Facade - closed", "material": "Steel sandwich panels", "cost_per_unit": 4, "unit": "m² closed"},
        {"category": "Facade - closed", "material": "Timber frame construction (HSB)", "cost_per_unit": 10, "unit": "m² closed"},
        {"category": "Other", "material": "n.a.", "cost_per_unit": 5, "unit": "m² total facade"},
        {"category": "Other", "material": "n.a.", "cost_per_unit": 5, "unit": "per facade"}
    ]
    _cost_table_category_options = ["Facade - open", "Facade - closed", "Other"]
    facade_size.data.cost_subtitle = vkt.Text("Initial cost data")
    facade_size.data.cost_table = vkt.Table("Initial cost table", default=_cost_table_default)
    facade_size.data.cost_table.category = vkt.OptionField("Category", options=_cost_table_category_options)
    facade_size.data.cost_table.material = vkt.TextField("Material")
    facade_size.data.cost_table.cost_per_unit = vkt.NumberField("Initial cost [€/unit]")
    facade_size.data.cost_table.unit = vkt.TextField("Unit")
    facade_size.data.cost_table.nmd_code = vkt.TextField("NMD code")

    # user-modifiable table for CO2 data
    _co2_table_default = [
        {"category": "Facade - open", "material": "Double glazing", "co2_per_unit": 50, "unit": "m² open", "nmd_code": "#nmd_00000"},
        {"category": "Facade - closed", "material": "Prefab concrete sandwich panels", "co2_per_unit": 40, "unit": "m² closed", "nmd_code": "#nmd_00000"},
        {"category": "Facade - closed", "material": "Steel sandwich panels", "co2_per_unit": 35, "unit": "m² closed", "nmd_code": "#nmd_00000"},
        {"category": "Facade - closed", "material": "Timber frame construction (HSB)", "co2_per_unit": 10, "unit": "m² closed", "nmd_code": "#nmd_00000"}
    ]
    _co2_table_category_options = ["Facade - open", "Facade - closed"]
    facade_size.data.co2_subtitle = vkt.Text("CO2 data")
    facade_size.data.co2_table = vkt.Table("cCO Table", default=_co2_table_default)
    facade_size.data.co2_table.category = vkt.OptionField("Category", options=_co2_table_category_options)
    facade_size.data.co2_table.material = vkt.TextField("Material")
    facade_size.data.co2_table.co2_per_unit = vkt.NumberField("CO2 [kg/unit]")
    facade_size.data.co2_table.unit = vkt.TextField("Unit")
    facade_size.data.co2_table.nmd_code = vkt.TextField("NMD code")


    result = vkt.Page("2. Overvew all options", views=['plotly_pcp_view'])  # showing the parallel coordinate plot

    configurations = vkt.Page("3. Visualisation selected option", views=['plotly_view', 'facade_2d_view'])
    configurations.facade_1 = vkt.Tab("Facade 1")
    configurations.facade_1.params = vkt.Section("Parameters")
    configurations.facade_1.params.wwr = vkt.NumberField("Window-wall ratio (WWR)", min=20, max=90, default=50, variant='slider', suffix='%')
    configurations.facade_1.params.lb1 = vkt.LineBreak()
    configurations.facade_1.params.lb11 = vkt.LineBreak()
    configurations.facade_1.params.material = vkt.OptionField("Material facade", default='Prefab concrete sandwich panels',
                                                              options=[
                                                                  "Prefab concrete sandwich panels",
                                                                  "Steel sandwich panels",
                                                                  "Timber frame construction (HSB)"
                                                              ])
    configurations.facade_1.params.lb2 = vkt.LineBreak()
    configurations.facade_1.params.lb22 = vkt.LineBreak()
    configurations.facade_1.params.sun_shading = vkt.BooleanField("Sun shading")
    configurations.facade_1.params.lb3 = vkt.LineBreak()
    configurations.facade_1.params.num_windows = vkt.IntegerField("Number of windows per storey", min=1, max=5, default=2)

    configurations.facade_2 = vkt.Tab("Facade 2")
    configurations.facade_2.params = vkt.Section("Parameters")
    configurations.facade_2.params.wwr = vkt.NumberField("Window-wall ratio (WWR)", min=20, max=90, default=50, variant='slider', suffix='%')
    configurations.facade_2.params.lb1 = vkt.LineBreak()
    configurations.facade_2.params.material = vkt.OptionField("Material facade", default='Steel sandwich panels',
                                                              options=[
                                                                  "Prefab concrete sandwich panels",
                                                                  "Steel sandwich panels",
                                                                  "Timber frame construction (HSB)"
                                                              ])
    configurations.facade_2.params.lb2 = vkt.LineBreak()
    configurations.facade_2.params.sun_shading = vkt.BooleanField("Sun shading")
    configurations.facade_2.params.lb3 = vkt.LineBreak()
    configurations.facade_2.params.num_windows = vkt.IntegerField("Number of windows per storey", min=1, max=5, default=2)

    configurations.facade_3 = vkt.Tab("Facade 3")
    configurations.facade_3.params = vkt.Section("Parameters")
    configurations.facade_3.params.wwr = vkt.NumberField("Window-wall ratio (WWR)", min=20, max=90, default=50, variant='slider', suffix='%')
    configurations.facade_3.params.lb1 = vkt.LineBreak()
    configurations.facade_3.params.material = vkt.OptionField("Material facade", default='Timber frame construction (HSB)',
                                                              options=[
                                                                  "Prefab concrete sandwich panels",
                                                                  "Steel sandwich panels",
                                                                  "Timber frame construction (HSB)"
                                                              ])
    configurations.facade_3.params.lb2 = vkt.LineBreak()
    configurations.facade_3.params.sun_shading = vkt.BooleanField("Sun shading")
    configurations.facade_3.params.lb3 = vkt.LineBreak()
    configurations.facade_3.params.num_windows = vkt.IntegerField("Number of windows per storey", min=1, max=5, default=2)



class Controller(vkt.Controller):
    label = "Facade Configuration"
    parametrization = Parametrization()

    # Define color codes for materials
    material_colors = {
        'Prefab concrete sandwich panels': vkt.Color(200, 200, 200),  # Light gray
        'Steel sandwich panels': vkt.Color(169, 169, 169),  # Dark gray
        'Timber frame construction (HSB)': vkt.Color(210, 180, 140)  # Tan
    }


    def calculate_outputs(self, facade_params, facade_size):

        # print("facade_size.data.mki_table.mki_per_unit:", facade_size.data.mki_table.mki_per_unit)
        print("facade_size.data.mki_table:", facade_size.data.mki_table)
        db_mki_table = facade_size.data.mki_table  # this is a list of Munch elements: [Munch({'category': 'Facade - open', 'material': 'Double glazing', ...
        db_cost_table = facade_size.data.cost_table
        db_co2_table = facade_size.data.co2_table

        # create df_options
        def sort_unique_facade_materials(db_table, mat_category_str, col_name_str):
            filtered_materials = [
                item for item in db_table
                if getattr(item, 'category', None) == mat_category_str and hasattr(item, col_name_str)
            ]
            sorted_materials = sorted(filtered_materials, key=lambda x: getattr(x, col_name_str))
            return [item.material for item in sorted_materials]

        unique_mat_open_sorted_mki = sort_unique_facade_materials(db_mki_table, "Facade - open", "mki_per_unit")
        unique_mat_close_sorted_mki = sort_unique_facade_materials(db_mki_table, "Facade - closed", "mki_per_unit")
        print(unique_mat_open_sorted_mki, unique_mat_close_sorted_mki)

        unique_mat_open_sorted_cost = sort_unique_facade_materials(db_cost_table, "Facade - open", "cost_per_unit")
        unique_mat_close_sorted_cost = sort_unique_facade_materials(db_cost_table, "Facade - closed", "cost_per_unit")
        print(unique_mat_open_sorted_cost, unique_mat_close_sorted_cost)

        unique_mat_open_sorted_co2 = sort_unique_facade_materials(db_co2_table, "Facade - open", "co2_per_unit")
        unique_mat_close_sorted_co2 = sort_unique_facade_materials(db_co2_table, "Facade - closed", "co2_per_unit")
        print(unique_mat_open_sorted_co2, unique_mat_close_sorted_co2)

        # wwr: ranging from 20 to 80 at interval of 20
        wwr_option_list = [20, 40, 60, 80]

        # column names of df_option
        col_name_all = [
            "facade_open",
            "facade_close",
            "wwr",
        ]
        allCombo = list(product(unique_mat_open_sorted_mki, unique_mat_close_sorted_mki, wwr_option_list
                                ))
        df_options_list = np.array(allCombo).T.tolist()
        df_options = pd.DataFrame({col_name_all[0]: df_options_list[0]})
        for i in range(len(col_name_all) - 1):
            df_options[col_name_all[i + 1]] = df_options_list[i + 1]

        print("df_options:")
        print(df_options.to_string())


        # # Example df_options
        # df_options = pd.DataFrame([
        #     {'facade_open': 'Double glazing', 'facade_close': 'Prefab concrete sandwich panels'},
        #     {'facade_open': 'Double glazing', 'facade_close': 'Timber frame construction (HSB)'}
        # ])

        # --- Quantity Constants ---
        area_facade_total = facade_size.dimensions.width * facade_size.dimensions.num_storeys * facade_size.dimensions.storey_height
        area_facade_open = area_facade_total * 20  # todo: to use wwr
        area_facade_close = area_facade_total * 80  # todo: to use wwr

        # --- Create Lookups ---
        mki_dict = {item.material: item.mki_per_unit for item in db_mki_table}
        cost_dict = {item.material: item.cost_per_unit for item in db_cost_table}
        co2_dict = {item.material: item.co2_per_unit for item in db_co2_table}
        unit_dict = {item.material: item.unit for item in db_mki_table}  # Prefer MKI unit, assume it's authoritative

        # --- Function to decide quantity based on unit ---
        def get_quantity_for_unit(unit: str) -> float:
            if unit == "m² open":
                return area_facade_open
            elif unit == "m² closed":
                return area_facade_close
            elif unit == "m² total facade":
                return area_facade_total
            else:
                return 2  # Default fallback

        # --- Row-wise computation ---
        def calculate_mki_cost_from_units(row):  # todo: use wwr
            total_mki = 0
            total_cost = 0
            total_co2 = 0
            for col in df_options.columns:
                material = row[col]
                unit = unit_dict.get(material, "")
                quantity = get_quantity_for_unit(unit)
                mki = mki_dict.get(material, 0)
                cost = cost_dict.get(material, 0)
                co2 = co2_dict.get(material, 0)
                total_mki += mki * quantity
                total_cost += cost * quantity
                total_co2 += co2 * quantity
            return pd.Series({'mki': total_mki, 'cost': total_cost, 'co2': total_co2})

        # --- Apply calculation ---
        df_options_results = df_options.apply(calculate_mki_cost_from_units, axis=1)

        # --- Output ---
        print(df_options_results)


        # Dummy coefficients for calculations
        wwr_coeff = {
            'cost': 450,
            'co2': 14.55,
            'energy': 1
        }
        material_coeff = {
            'Prefab concrete sandwich panels': {'cost': 0.1, 'co2': 0.2, 'energy': 0.1},
            'Steel sandwich panels': {'cost': 0.15, 'co2': 0.25, 'energy': 0.15},
            'Timber frame construction (HSB)': {'cost': 0.05, 'co2': 0.1, 'energy': 0.05}
        }
        sun_shading_coeff = {
            'cost': 14.55,
            'co2': 0.1,
            'energy': 0.3
        }

        # Calculate facade total area
        facade_total_area = facade_size.dimensions.width * facade_size.dimensions.num_storeys * facade_size.dimensions.storey_height

        # Calculate outputs
        initial_cost = wwr_coeff['cost'] * facade_params.params.wwr * facade_total_area / 100 \
                       + material_coeff[facade_params.params.material]['cost'] * 100
        embedded_co2 = wwr_coeff['co2'] * facade_params.params.wwr * facade_total_area / 100 \
                       + material_coeff[facade_params.params.material]['co2'] * 100
        energy_use = wwr_coeff['energy'] * facade_params.params.wwr * facade_total_area / 100 \
                     + material_coeff[facade_params.params.material]['energy'] * 100

        if facade_params.params.sun_shading:
            initial_cost += sun_shading_coeff['cost'] * 100
            embedded_co2 += sun_shading_coeff['co2'] * 100
            energy_use -= sun_shading_coeff['energy'] * 100  # Sun shading reduces energy use

        return initial_cost, embedded_co2, energy_use, df_options_results, df_options




    @PlotlyView("Output Visualization", duration_guess=1)
    def plotly_pcp_view(self, params, **kwargs):
        facades = [params.configurations.facade_1, params.configurations.facade_2, params.configurations.facade_3]
        facade_names = ['Facade 1', 'Facade 2', 'Facade 3']

        initial_costs = []
        embedded_co2s = []
        energy_uses = []





        for facade in facades:
            initial_cost, embedded_co2, energy_use, df_options_results, df_options = self.calculate_outputs(facade, params.facade_size)
            initial_costs.append(initial_cost)
            embedded_co2s.append(embedded_co2)
            energy_uses.append(energy_use)

        print("type df_options_results['mki']:", type(df_options_results['mki']), df_options_results['mki'])

        # add index of options to the plot as a separate column
        option_idx = pd.Series(range(len(df_options)))

        # Create subplots
        fig = go.Figure(data=
            go.Parcoords(
                line_color='blue',
                dimensions=list([
                    dict(
                        multiselect=False,
                        label="MKI [€]",
                        values=df_options_results['mki']),
                    dict(
                        multiselect=False,
                        label="Cost [€]",
                        values=df_options_results['cost']),
                    dict(
                        multiselect=False,
                        label="CO2 [kg]",
                        values=df_options_results['co2']),
                    dict(
                        multiselect=False,
                        label="Option",
                        values=option_idx),
                    # dict(range=[1, 5],
                    #      tickvals=[1, 2, 4, 5],
                    #      label='C', values=[2, 4],
                    #      ticktext=['text 1', 'text 2', 'text 3', 'text 4']),
                    # dict(range=[1, 5],
                    #      label='D', values=[4, 2])
                ])
            )
            )

        return PlotlyResult(fig.to_json())





    @PlotlyView("Output Visualization", duration_guess=1)
    def plotly_view(self, params, **kwargs):
        facades = [params.configurations.facade_1, params.configurations.facade_2, params.configurations.facade_3]
        facade_names = ['Facade 1', 'Facade 2', 'Facade 3']

        initial_costs = []
        embedded_co2s = []
        energy_uses = []

        for facade in facades:
            initial_cost, embedded_co2, energy_use, df_options_results, df_options = self.calculate_outputs(facade, params.facade_size)
            initial_costs.append(initial_cost)
            embedded_co2s.append(embedded_co2)
            energy_uses.append(energy_use)

        # Create subplots
        fig = make_subplots(rows=3, cols=1,
                            subplot_titles=("Initial Cost (€/m²)",
                                            "Embedded CO2 (kg CO2/m²)",
                                            "Energy Use (kWh/yr/m²)"))

        # Initial Cost chart
        fig.add_trace(go.Bar(
            x=facade_names,
            y=initial_costs,
            name='Initial Cost',
            marker_color=vkt.Color(30, 144, 255).hex
        ), row=1, col=1)

        # Embedded CO2 chart
        fig.add_trace(go.Bar(
            x=facade_names,
            y=embedded_co2s,
            name='Embedded CO2',
            marker_color=vkt.Color(34, 139, 34).hex
        ), row=2, col=1)

        # Energy Use chart
        fig.add_trace(go.Bar(
            x=facade_names,
            y=energy_uses,
            name='Energy Use',
            marker_color=vkt.Color(255, 69, 0).hex
        ), row=3, col=1)

        # Update layout
        fig.update_layout(
            height=900,  # Increase height to accommodate three subplots
            title_text="Facade Performance Metrics Comparison",
            showlegend=False,
            plot_bgcolor="white",  # ← sets each subplot's background
        )

        # Update y-axes labels
        fig.update_yaxes(title_text="€/m²", row=1, col=1)
        fig.update_yaxes(title_text="kg CO2/m²", row=2, col=1)
        fig.update_yaxes(title_text="kWh/yr/m²", row=3, col=1)

        return PlotlyResult(fig.to_json())

    @PlotlyView("2D Facade View", duration_guess=1)
    def facade_2d_view(self, params, **kwargs):
        # Create a new figure
        fig = go.Figure()

        # Set up dimensions
        width = params.facade_size.dimensions.width
        height = params.facade_size.dimensions.num_storeys * params.facade_size.dimensions.storey_height

        # Calculate the total width including spacing
        total_width = 3 * width + 2 * 5  # 3 facades + 2 spaces of 5 meters

        # Draw walls and windows for each facade
        for i, facade in enumerate([params.configurations.facade_1, params.configurations.facade_2, params.configurations.facade_3]):
            # Calculate the x-coordinate for each facade, including spacing
            facade_x = i * (width + 5)

            # Get the color for the current facade material
            facade_color = self.material_colors[facade.params.material]

            # Draw the wall
            fig.add_shape(
                type="rect",
                x0=facade_x, y0=0, x1=facade_x + width, y1=height,
                line=dict(color=facade_color.hex, width=2),
                fillcolor=facade_color.hex,
            )

            window_area = (facade.params.wwr / 100) * width * params.facade_size.dimensions.storey_height
            window_width = min(np.sqrt(window_area / facade.params.num_windows), width / facade.params.num_windows)
            window_height = min(window_area / (facade.params.num_windows * window_width), params.facade_size.dimensions.storey_height)

            for floor in range(params.facade_size.dimensions.num_storeys):
                for window in range(facade.params.num_windows):
                    x0 = facade_x + (width / (facade.params.num_windows + 1)) * (window + 1) - window_width / 2
                    y0 = floor * params.facade_size.dimensions.storey_height + (params.facade_size.dimensions.storey_height - window_height) / 2
                    x1 = x0 + window_width
                    y1 = y0 + window_height

                    # Ensure window is within wall boundaries
                    x0 = max(x0, facade_x)
                    x1 = min(x1, facade_x + width)
                    y0 = max(y0, floor * params.facade_size.dimensions.storey_height)
                    y1 = min(y1, (floor + 1) * params.facade_size.dimensions.storey_height)

                    # Draw window frame
                    fig.add_shape(
                        type="rect",
                        x0=x0, y0=y0, x1=x1, y1=y1,
                        line=dict(color="darkgray", width=2),
                        fillcolor="white",
                    )

                    # Draw window glass
                    frame_width = 0.05  # 5% of window width for frame
                    fig.add_shape(
                        type="rect",
                        x0=x0 + window_width * frame_width,
                        y0=y0 + window_height * frame_width,
                        x1=x1 - window_width * frame_width,
                        y1=y1 - window_height * frame_width,
                        line=dict(color="lightblue", width=1),
                        fillcolor="lightblue",
                    )

            # Add sun shading if enabled
            if facade.params.sun_shading:
                for floor in range(params.facade_size.dimensions.num_storeys):
                    y = (floor + 1) * params.facade_size.dimensions.storey_height
                    fig.add_shape(
                        type="line",
                        x0=facade_x, y0=y, x1=facade_x + width, y1=y,
                        line=dict(color="darkgray", width=3),
                    )

            # Add facade label
            fig.add_annotation(
                x=facade_x + width / 2,
                y=height + 0.5,
                text=f"Facade {i + 1}",
                showarrow=False,
                font=dict(size=16, color="black"),
            )

        # Update layout
        fig.update_layout(
            title="2D Facade View",
            showlegend=False,
            paper_bgcolor='rgba(0, 0, 0, 0)',
            plot_bgcolor='rgba(0, 0, 0, 0)',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, total_width]),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x", scaleratio=1),
            width=1200,
            height=600,
        )

        return PlotlyResult(fig.to_json())



