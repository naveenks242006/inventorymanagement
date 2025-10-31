package main.java;

import static spark.Spark.*;
import java.util.*;
import spark.ModelAndView;
import spark.template.velocity.VelocityTemplateEngine;

public class Main {
    public static void main(String[] args) {
        port(8080); // server runs on localhost:8080

        // In-memory inventory
        List<Map<String, String>> items = new ArrayList<>();

        // Show HTML form
        get("/", (req, res) -> {
            StringBuilder html = new StringBuilder();
            html.append("<html><body style='font-family:Arial;margin:40px;'>");
            html.append("<h2>Inventory</h2>");
            html.append("<form action='/add' method='post'>");
            html.append("Item Name: <input name='name'><br><br>");
            html.append("Quantity: <input name='qty' type='number'><br><br>");
            html.append("<button>Add Item</button></form><br>");
            html.append("<h3>Items:</h3><ul>");
            for (Map<String, String> item : items) {
                html.append("<li>" + item.get("name") + " - " + item.get("qty") + "</li>");
            }
            html.append("</ul></body></html>");
            return html.toString();
        });

        // Handle form submission
        post("/add", (req, res) -> {
            Map<String, String> item = new HashMap<>();
            item.put("name", req.queryParams("name"));
            item.put("qty", req.queryParams("qty"));
            items.add(item);
            res.redirect("/");
            return null;
        });
    }
}
