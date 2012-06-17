
pft.directives = angular.module('pft.directives', ['ngResource']);


pft.directives.directive('pftDialog', function() {
  return {
    link: function(scope, element, attrs) {
      $(element).dialog({
          resizable: false,
          title: attrs.title,
          buttons: {
            'Save': function() {
              $(this).dialog('close');
            },
            'Cancel': function() {
              $(this).dialog('close');
            }
          }
      });
    }
  }
});


pft.directives.directive('pftEditCategoryDialog', function() {
  return {
    link: function(scope, element, attrs) {
      $(element).dialog({
          resizable: false,
          title: attrs.title,
          buttons: {
            'Save': function() {
              $(this).dialog('close');
            },
            'Cancel': function() {
              $(this).dialog('close');
            }
          }
      });
    }
  }
});


pft.directives.directive('pftButton', function() {
  return {
    link: function(scope, element, attrs) {
      var options = {
        'icons': {}
      };
      if (attrs.icon) {
        options['icons']['primary'] = attrs.icon;
      }
      if (attrs.icon_secondary) {
        options['icons']['secondary'] = attrs.icon_secondary;
      }
      $(element).button(options);
    }
  }
});


pft.directives.directive('pftCategoriesWidget', function() {
  return {
    templateUrl: '/a/categories_widget.html'
  }
});


pft.directives.directive('pftAccountsWidget', function() {
  return {
    templateUrl: '/a/accounts_widget.html'
  }
});
