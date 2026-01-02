document.addEventListener("DOMContentLoaded", function() {
    const planSelect = document.querySelector("#id_plan");
    const customModulesRow = document.querySelector(".form-row.field-custom_modules");

    function toggleCustomModules() {
        if (!planSelect || !customModulesRow) return;
        const selectedPlanText = planSelect.options[planSelect.selectedIndex].text.toLowerCase();
        if (selectedPlanText.includes("custom")) {
            customModulesRow.style.display = "block";
        } else {
            customModulesRow.style.display = "none";
        }
    }

    toggleCustomModules();
    planSelect.addEventListener("change", toggleCustomModules);
});
