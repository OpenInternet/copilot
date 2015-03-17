/*
    <div class="base_class" id="rules-2-group">
            <table id="rules-2"><tr><th><label for="rules-2-csrf_token">Csrf Token</label></th><td><input id="rules-2-csrf_token" name="rules-2-csrf_token" type="hidden" value="1426626216##f5ebfe1f39eb13480e52e581f84f050bafdbb6ad"></td></tr><tr><th><label for="rules-2-action">Action</label></th><td><select id="rules-2-action" name="rules-2-action"><option selected value="block">block</option></select></td></tr><tr><th><label for="rules-2-target">Target</label></th><td><select id="rules-2-target" name="rules-2-target"><option selected value="dns">dns</option><option value="url">url</option></select></td></tr><tr><th><label for="rules-2-sub_target">Sub-Target</label></th><td><input id="rules-2-sub_target" name="rules-2-sub_target" type="text" value="frank"></td></tr></table>
            <button data-field="rules-2-group">Remove Entry</button>
    </div> 
 */

empty_rule = document.createElement("div");


list = document.getElementById("rule_list");
list.appendChild(empty_rule);
