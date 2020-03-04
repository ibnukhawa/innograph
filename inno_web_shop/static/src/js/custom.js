odoo.define('inno_web_shop.add_to_cart', function (require) {
    "use strict";
var core = require('web.core');
var qweb = core.qweb;

    $(document).ready(function() {

        $(".btn-add-to-cart").click(function(event){
            var product_id = $(this).attr("id");
            
            $.get("/shop/cart/update_click/"+product_id, function( data ) {
                var append_item = ""
                $(".cart_quantity").html(data.jumlah_qty);

                var window_width =$( window ).width();
                var class_name = "cart_quantity";

                if(window_width < 992){
                    class_name = "span-cart";
                }


                $('.'+class_name).addClass('o_shadow_animation_cart').delay(700).queue(function(){
                    $(this).removeClass("o_shadow_animation_cart").dequeue();
                });
                


                var imgtodrag = $(event.target).closest('form').find('img').eq(0);
                if (imgtodrag.length) {
                    var imgclone = imgtodrag.clone()
                    .offset({
                        top: imgtodrag.offset().top,
                        left: imgtodrag.offset().left
                    })
                    .addClass('o_product_comparison_animate')
                    .appendTo($('body'))
                    .animate({
                        'top': $("."+class_name).offset().top,
                        'left': $("."+class_name).offset().left,
                        'width': 75,
                        'height': 75
                    }, 1000, 'easeInOutExpo');

                    imgclone.animate({
                        'width': 0,
                        'height': 0
                    });
                }
                if (data.jumlah_data_awal < 1){
                    append_item += "<div style='background-color:#f5f5f5;'>";
                    append_item += "<span class='hci-row' style='margin: 20px;line-height: 3;'> Troli Belanja";
                    append_item += "</span>";
                    append_item += "</div>";
                    append_item += "<div style='overflow: scroll; height: 300px;' class='item-dropdown-cart'>";
                    
                    append_item += "<li>";
                    append_item += "<div class='items' style='width:300px;'>";
                    append_item += "<span class='items-info'>";
                    append_item += "<table style='width:100%;'>";
                    append_item += "<tbody>";
                    append_item += "<tr>";
                    append_item += "<td style='width: 40%;margin-right: 10px;'>";
                    append_item += "<center>";
                    append_item += "<a href='/shop/product/"+data.url_name+"-"+data.product_id+"'>";
                    append_item += "<span>";
                    append_item += "<img class='img img-responsive img-responsive' src='"+data.image_small+"'>";
                    append_item += "</img>";
                    append_item += "</span>";
                    append_item += "</a>";
                    append_item += "</center>";
                    append_item += "</td>";
                    append_item += "<td>";

                    append_item += "<label class='names'>";
                    append_item += "<a href='/shop/product/"+data.url_name+"-"+data.product_id+"'>";
                    append_item += "<strong style='font-weight: 400;'> "+data.display_name;
                    append_item += "</strong>";
                    append_item += "</a>";
                    append_item += "</label>";

                    append_item += "<label class='quantitys "+data.product_id_awal+"' id='"+data.qty+"'> "+data.qty+" x   ";
                    append_item += "</label>";
                    append_item += "<label class='totals'>";
                    append_item += "<span style='white-space: nowrap;'> "+data.price;
                    append_item += "</span>";
                    append_item += "</label>";

                    append_item += "</td>";
                    append_item += "</tr>";
                    append_item += "</tbody>";
                    append_item += "</table>";
                    append_item += "</span>";
                    append_item += "</div>";
                    append_item += "<hr/>";
                    append_item += "</li>";

                    append_item += "</div>";
                    
                    append_item += "<div class='cart-summary'>";
                    append_item += "<p class='cart-total'>";
                    append_item += "<span class='label' style='color:#000;font-weight:400; font-size:12px;'> Total:";
                    append_item += "</span>";
                    append_item += "<span class='price' style='white-space: nowrap'> "+data.amount_total;
                    append_item += "</span>";
                    append_item += "</p>";
                    append_item += "</div>";
                    
                    append_item += "<hr/>";

                    append_item += "<div class='cart-actions' style='float:right; margin-right: 20px; margin-bottom: 20px;'>";
                    append_item += "<a href='/shop/cart' class='btn btn-primary'>";
                    append_item += "<div class='view-carts'> Checkout";
                    append_item += "</div>";
                    append_item += "</a>";
                    append_item += "</div>";
                    
                    $(".dropdown-carts-view").removeClass("troli-empty");
                    $(".dropdown-carts-view").addClass("troli");
                    $(".dropdown-carts-view").html(append_item);
                }
                else{

                    $(".price").html(data.amount_total);
                    if(data.status == "update"){
                        var qty_awal = $("."+product_id).attr("id");
                        var qty_update = parseInt(qty_awal) + 1;
                        
                        $("."+product_id).html(qty_update+".0 x &nbsp;");

                        var qty_awal = $("."+product_id).attr("id",qty_update);
                    }
                    else if(data.status == 'add'){
                        append_item += "<li>";
                        append_item += "<div class='items' style='width:300px;'>";
                        append_item += "<span class='items-info'>";
                        append_item += "<table style='width:100%;'>";
                        append_item += "<tbody>";
                        append_item += "<tr>";
                        append_item += "<td style='width: 40%;margin-right: 10px;'>";
                        append_item += "<center>";
                        append_item += "<a href='/shop/product/"+data.url_name+"-"+data.product_id+"'>";
                        append_item += "<span>";
                        append_item += "<img class='img img-responsive img-responsive' src='"+data.image_small+"'>";
                        append_item += "</img>";
                        append_item += "</span>";
                        append_item += "</a>";
                        append_item += "</center>";
                        append_item += "</td>";
                        append_item += "<td>";
    
                        append_item += "<label class='names'>";
                        append_item += "<a href='/shop/product/"+data.url_name+"-"+data.product_id+"'>";
                        append_item += "<strong style='font-weight: 400;'> "+data.display_name;
                        append_item += "</strong>";
                        append_item += "</a>";
                        append_item += "</label>";
    
                        append_item += "<label class='quantitys "+data.product_id_awal+"' id='"+data.qty+"'> "+data.qty+" x &nbsp;	";
                        append_item += "</label>";
                        append_item += "<label class='totals'>";
                        append_item += "<span style='white-space: nowrap;'> "+data.price;
                        append_item += "</span>";
                        append_item += "</label>";
    
                        append_item += "</td>";
                        append_item += "</tr>";
                        append_item += "</tbody>";
                        append_item += "</table>";
                        append_item += "</span>";
                        append_item += "</div>";
                        append_item += "<hr/>";
                        append_item += "</li>";
    
                        $(".item-dropdown-cart").append(append_item);
                        
                }

                }
                
            });
        
        });

    });
});