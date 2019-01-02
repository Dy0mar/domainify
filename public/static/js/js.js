/**
 * Closest fn
 * old browsers support
 */
if(window.Element){
    if (!Element.prototype.matches)
        Element.prototype.matches = Element.prototype.msMatchesSelector ||
            Element.prototype.webkitMatchesSelector;

    if (!Element.prototype.closest)
        Element.prototype.closest = function(s) {
            var el = this;
            if (!document.documentElement.contains(el)) return null;
            do {
                if (el.matches(s)) return el;
                el = el.parentElement || el.parentNode;
            } while (el !== null && el.nodeType === 1);
            return null;
        };
}
/**
 * document loading states
 */
document.addEventListener('readystatechange',function(){
    /**
     * loading
     * The document is still loading.
     *
     * interactive
     * The document has finished loading and the document has been parsed but sub-resources such as images, stylesheets and frames are still loading.
     *
     * compvare
     * The document and all sub-resources have finished loading. The state indicates that the load event is about to fire.
     */
    if (document.readyState === "loading") {

    }
    if (document.readyState === "interactive") {
        listeners(document);
        document.addEventListener('click',function(ev){
            //close all dropdowns
            evCloseDropdowns(ev,this);
        });
        //pretty selects
        $('select').selectmenu({
            classes: {
                "ui-selectmenu-button": "form-control"
            }
        });
    }
    if (document.readyState === "complete") {

    }
});
function evCloseDropdowns(ev,cur){
    var drp = document.querySelectorAll('.mydropdown.active,.mydropdown-toggle.active');
    for (var i=0; i<drp.length; i++){
        cur !== drp[i] && drp[i].classList.remove('active');
    }
}
/**
 * Events
 * @param container
 */
function listeners(container){
    /**
     * Dropdowns
     * @type {NodeList}
     */
    var drops = container.querySelectorAll('.mydropdown');
    if(drops.length){
        for(var i=0;i<drops.length;i++){
            //container
            drops[i].addEventListener('click',function (ev) {
                ev.stopPropagation();
            });
            //toggles
            var toggle = drops[i].querySelectorAll('.mydropdown-toggle');
            if(toggle.length){
                for(var j=0;j<toggle.length;j++){
                    toggle[j].addEventListener('click',function(ev){
                        ev.preventDefault();
                        var dropContainer = this.closest('.mydropdown');
                        var dropBtn = dropContainer.querySelectorAll('.mydropdown-toggle');
                        !this.classList.contains('active') && evCloseDropdowns(ev,{});
                        dropContainer.classList.toggle('active');
                        if(dropBtn.length){
                            for(var n=0;n<dropBtn.length;n++){
                                dropBtn[n].classList.toggle('active');
                            }
                        }
                    });
                }
            }
            //menus
        }
    }
    /**
     * datapiker
     */
    $('.js-datepicker').datepicker({
        altFormat: "dd.mm.yyyy",
        dateFormat: "dd.mm.yy",
        changeYear: true
    });
    var dtPk = container.querySelector('.datepicker.dropdown-menu');
    if(dtPk){
        dtPk.addEventListener('click',function (ev) {
            ev.stopPropagation();
        });
    }
}
