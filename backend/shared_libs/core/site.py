from django.contrib import admin

class GroupedAdminSite(admin.AdminSite):
    site_header = "Monorepo Admin"

    def get_app_list(self, request, app_label=None):
        """
        Custom logic to group models into virtual 'apps'.
        """
        app_dict = self._build_app_dict(request)

        custom_groups = {
            'Logs': ['AuditLog'],
            'Authentication': ['User', 'UserRole', 'Role', 'Permission'],
            'Users': ['CustomerProfile', 'Address', 'City', 'Province', 'Wallet', 'WalletTransaction'],
            'Orders': ['Order', 'OrderItem', 'OrderItemFile', 'OrderStatus', 'OrderStatusGroup', 'OrderCostSheet', 'OrderCostItem', 'OrderCostReport', 'OrderPrintItem', 'OrderCostType', 'OrderPrintAttachment', 'OrderSchedule'],
            'Products': ['Product', 'ProductCategory', 'ProductOption', 'ProductOptionValue', 'ProductOptionPricingStrategy', 'ProductOptionInputType'],
            'Financial': ['Transaction', 'Quotation', 'QuotationStatus', 'QuotationStatusGroup', 'Invoice', 'InvoiceItem', 'InvoiceStatus', 'InvoiceStatusGroup'],
        }

        new_app_list = []

        for group_name, models_in_group in custom_groups.items():
            group_models = []
            
            for app in app_dict.values():
                for model in app['models']:
                    if model['object_name'] in models_in_group:
                        group_models.append(model)

            if group_models:
                new_app_list.append({
                    'name': group_name,
                    'app_label': group_name.lower().replace(' ', '_'),
                    'models': sorted(group_models, key=lambda x: x['name']),
                    'has_module_perms': True,
                })

        return new_app_list

custom_admin_site = GroupedAdminSite(name='custom_admin')
