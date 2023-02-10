from deploy_kit import ProductionErrorKit




prod = ProductionErrorKit(__name__, "test")
prod.enable_production_exception_mode()

raise MemoryError

