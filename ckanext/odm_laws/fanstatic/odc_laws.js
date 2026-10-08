// ODC-specific law page JavaScript for animations and filter interactions
$(document).ready(function () {
  // ============================================
  // Shared Helper Functions (top-level scope)
  // ============================================

  function getTranslation(key, count) {
    var lang = $("html").attr("lang") || "en";
    var translations = {
      selected: {
        km: "បានជ្រើសរើស %s",
        my: "%s ခု ရွေးချယ်ထားသည်",
        lo: "%s ເລືອກແລ້ວ",
        vi: "%s đã chọn",
        th: "%s เลือกแล้ว",
        en: "%s selected",
      },
      show_more: {
        km: "មើលបន្ថែម (%s) ",
        my: "ပိုမိုကြည့်ရှုရန် (%s) ",
        lo: "ສະແດງເພີ່ມເຕີມ (%s) ",
        vi: "Xem thêm (%s) ",
        th: "แสดงเพิ่มเติม (%s) ",
        en: "Show more (%s) ",
      },
      show_less: {
        km: "មើលតិចជាង ",
        my: "နည်းနည်းကြည့်ရှုရန် ",
        lo: "ສະແດງໜ້ອຍລົງ ",
        vi: "Thu gọn ",
        th: "แสดงน้อยลง ",
        en: "Show less ",
      },
      copied: {
        km: "បានចម្លង",
        my: "ကူးယူပြီးပါပြီ",
        lo: "ສຳເນົາແລ້ວ",
        vi: "Đã sao chép",
        th: "คัดลอกแล้ว",
        en: "Copied",
      },
    };
    var pattern =
      (translations[key] &&
        (translations[key][lang] || translations[key]["en"])) ||
      "";
    return count !== undefined ? pattern.replace("%s", count) : pattern;
  }

  function updateHiddenItems($section) {
    var $optionsContainer = $section.find(".filter-options");
    var $allOptions = $optionsContainer.find(".filter-option");
    var $showMoreButton = $optionsContainer.find(".show-more-filters");
    var isExpanded = $showMoreButton.hasClass("show-less");

    $allOptions.each(function (index) {
      var $option = $(this);
      var shouldBeHidden =
        index >= 5 && !$option.hasClass("active") && !isExpanded;
      if (shouldBeHidden) {
        $option.addClass("filter-option-hidden");
      } else {
        $option.removeClass("filter-option-hidden");
      }
      $option.removeAttr("style");
    });

    var hiddenCount = $allOptions.filter(function (index) {
      return index >= 5 && !$(this).hasClass("active");
    }).length;

    if (hiddenCount > 0) {
      $showMoreButton.show();
      $showMoreButton.data("count", hiddenCount);
      if (!isExpanded) {
        var textNode = $showMoreButton.contents().filter(function () {
          return this.nodeType === 3;
        })[0];
        if (textNode) {
          textNode.textContent = getTranslation("show_more", hiddenCount);
        }
      }
    } else {
      $showMoreButton.hide();
    }
  }

  function updateFilterCounts() {
    $(".filter-section").each(function () {
      var $section = $(this);
      var activeCount = $section.find(".filter-option.active").length;
      var $countSpan = $section.find(".filter-count");

      if (activeCount > 0) {
        var translatedText = getTranslation("selected", activeCount);
        if ($countSpan.length === 0) {
          $section
            .find(".filter-toggle")
            .append('<span class="filter-count">' + translatedText + "</span>");
        } else {
          $countSpan.text(translatedText);
        }
      } else {
        $countSpan.remove();
      }
    });
  }

  // ============================================
  // ODC Law Detail Page Functionality
  // ============================================

  // Share button — copy current page URL to clipboard
  $(document).on("click", ".odc-header-share-btn", function () {
    var $btn = $(this);
    var url = window.location.href;
    var originalHtml = $btn.html();

    function done(feedback) {
      $btn.html('<i class="fa fa-check"></i> ' + feedback);
      setTimeout(function () {
        $btn.html(originalHtml);
      }, 2000);
    }

    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(
        function () {
          done(getTranslation("copied") || "Copied");
        },
        function () {
          fallbackCopy(url, done);
        },
      );
    } else {
      fallbackCopy(url, done);
    }

    function fallbackCopy(text, done) {
      var $ta = $("<textarea>")
        .val(text)
        .css({ position: "fixed", opacity: "0" })
        .appendTo("body");
      $ta.select();
      try {
        document.execCommand("copy");
        done(getTranslation("copied") || "Copied");
      } catch (e) {
        window.prompt("Copy link:", text);
      } finally {
        $ta.remove();
      }
    }
  });

  function resizeSortingDropdown() {
    var $select = $("#sorting-dropdown");
    var $tester = $("#width-tester");
    var selectedText = $select.find("option:selected").text();
    $tester.text(selectedText);
    var newWidth = $tester.width() + 35;
    $select.css("width", newWidth + "px");
  }

  resizeSortingDropdown();
  $("#sorting-dropdown").on("change", resizeSortingDropdown);

  if ($(".odc-law-details").length) {
    $(".odc-law-details").hide().fadeIn(1000);
  }

  if ($(".odc-law-nav a").length) {
    $(".odc-law-nav a").click(function (e) {
      e.preventDefault();
      var target = $(this).attr("href");
      $("html, body").animate({ scrollTop: $(target).offset().top - 100 }, 500);
    });
  }

  if ($(".odc-law-resource").length) {
    $(".odc-law-resource").hover(
      function () {
        $(this).addClass("odc-resource-hover");
      },
      function () {
        $(this).removeClass("odc-resource-hover");
      },
    );
  }

  if ($(".odc-law-meta-toggle").length) {
    $(".odc-law-meta-toggle").click(function () {
      $(".odc-law-meta-details").slideToggle();
      $(this).find("i").toggleClass("fa-chevron-down fa-chevron-up");
    });
  }

  if ($(".odc-print-law").length) {
    $(".odc-print-law").click(function () {
      window.print();
      return false;
    });
  }

  if ($('[data-toggle="odc-tooltip"]').length) {
    $('[data-toggle="odc-tooltip"]').tooltip({
      placement: "top",
      trigger: "hover",
    });
  }

  // ============================================
  // ODC Law Search Filter Interactions
  // ============================================

  if ($(".filter-toggle").length) {
    console.log("[ODC] Filter toggles found:", $(".filter-toggle").length);

    // Toggle filter sections open/closed
    $(".filter-toggle").on("click", function (e) {
      e.preventDefault();
      var $toggle = $(this);
      var $options = $toggle.closest(".filter-section").find(".filter-options");
      var $icon = $toggle.find(".filter-icon");

      if ($options.is(":visible")) {
        $options.stop(true, true).slideUp(200);
        $toggle.attr("aria-expanded", "false");
        $icon.css("transform", "rotate(0deg)");
      } else {
        $options.stop(true, true).slideDown(200);
        $toggle.attr("aria-expanded", "true");
        $icon.css("transform", "rotate(180deg)");
      }
    });

    console.log("[ODC] Filter options found:", $(".filter-option").length);

    // Handle filter checkbox clicks
    $(".filter-option").click(function (e) {
      e.preventDefault();
      e.stopPropagation();

      var $option = $(this);
      var $checkbox = $option.find(".facet-checkbox");
      var facetName = $checkbox.attr("name");
      var facetValue = $checkbox.val();

      console.log(
        "[ODC] Filter clicked:",
        facetName,
        "=",
        facetValue,
        "target:",
        e.target.tagName,
        e.target.className,
      );

      if ($(e.target).is("input")) {
        return;
      }

      // Handle "All" option
      if (facetValue === "__all__") {
        console.log("[ODC] Clearing all filters for:", facetName);
        $option
          .closest(".filter-section")
          .find('.facet-checkbox[value!="__all__"]')
          .prop("checked", false);
        var clearUrl =
          window.location.pathname +
          "?" +
          $.param(removeParamFromQuery(facetName));
        window.location.href = clearUrl;
        return;
      }

      var isChecked = !$checkbox.prop("checked");
      $checkbox.prop("checked", isChecked);

      if (isChecked) {
        console.log("[ODC] Adding filter:", facetName, "=", facetValue);
        $option.addClass("active");
        $option.find(".filter-checkbox-icon").addClass("checked");
        $option
          .find(".checkbox-box")
          .css("fill", "#4ade80")
          .css("stroke", "#4ade80");

        var url = $checkbox.data("add-url");
        console.log("[ODC] Add URL:", url);
        if (!url) {
          var params = getQueryParams();
          params[facetName] = facetValue;
          url = window.location.pathname + "?" + $.param(params);
          console.log("[ODC] Constructed URL:", url);
        }
        console.log("[ODC] Navigating to:", url);
        window.location.href = url;
      } else {
        console.log("[ODC] Removing filter:", facetName, "=", facetValue);
        $option.removeClass("active");
        $option.find(".filter-checkbox-icon").removeClass("checked");
        $option.find(".checkbox-box").css("fill", "").css("stroke", "#d1d5db");

        var url = $checkbox.data("remove-url");
        console.log("[ODC] Remove URL:", url);
        if (!url) {
          var params = getQueryParams();
          delete params[facetName];
          url = window.location.pathname + "?" + $.param(params);
          console.log("[ODC] Constructed URL:", url);
        }
        console.log("[ODC] Navigating to:", url);
        window.location.href = url;
      }
    });

    // Update filter counts when page loads
    updateFilterCounts();

    // Helper function to get query parameters as object
    function getQueryParams() {
      var params = {};
      var queryString = window.location.search.substring(1);
      var pairs = queryString.split("&");
      for (var i = 0; i < pairs.length; i++) {
        var pair = pairs[i].split("=");
        if (pair[0]) {
          params[decodeURIComponent(pair[0])] = decodeURIComponent(
            pair[1] || "",
          );
        }
      }
      return params;
    }

    // Helper function to remove a parameter from query string
    function removeParamFromQuery(paramName) {
      var params = getQueryParams();
      delete params[paramName];
      return params;
    }
  } // End of if ($('.filter-toggle').length) check

  // ============================================
  // Mobile Sidebar / Filter Panel Functionality
  // ============================================

  var $mobileSidebar = $("#mobileSidebar");
  var $sidebarOverlay = $("#sidebarOverlay");
  var $mobileFilterBtn = $("#mobileFilterBtn");
  var $closeSidebarBtn = $("#closeSidebarBtn");

  if ($mobileFilterBtn.length) {
    $mobileFilterBtn.click(function () {
      console.log("[ODC] Opening mobile sidebar");
      $mobileSidebar.addClass("mobile-open");
      $sidebarOverlay.addClass("active");
      $("body").css("overflow", "hidden");
    });
  }

  function closeMobileSidebar() {
    console.log("[ODC] Closing mobile sidebar");
    $mobileSidebar.removeClass("mobile-open");
    $sidebarOverlay.removeClass("active");
    $("body").css("overflow", "");
  }

  if ($closeSidebarBtn.length) {
    $closeSidebarBtn.click(function () {
      closeMobileSidebar();
    });
  }

  if ($sidebarOverlay.length) {
    $sidebarOverlay.click(function () {
      closeMobileSidebar();
    });
  }

  if ($mobileSidebar.length) {
    $mobileSidebar.find(".filter-option").click(function () {
      if (window.innerWidth <= 1024) {
        setTimeout(function () {
          closeMobileSidebar();
        }, 300);
      }
    });
  }

  $(document).keydown(function (e) {
    if (e.key === "Escape" && $mobileSidebar.hasClass("mobile-open")) {
      closeMobileSidebar();
    }
  });

  // ============================================
  // Handle search form submission
  // ============================================

  if ($(".odc-search-bar form").length) {
    $(".odc-search-bar form").submit(function (e) {
      var $input = $(this).find('input[name="q"]');
      $input.val($.trim($input.val()));
      if (!$input.val()) {
        e.preventDefault();
        window.location.href = window.location.pathname;
      }
    });

    $(".search-button").click(function () {
      $(".odc-search-bar form").submit();
    });

    $(".search-input").keypress(function (e) {
      if (e.which === 13) {
        $(".odc-search-bar form").submit();
        return false;
      }
    });
  }

  // ============================================
  // Facet Options Search
  // ============================================

  $(".facet-search-input").on("keyup", function () {
    var $input = $(this);
    var filterValue = $input.val().toLowerCase();
    var $optionsContainer = $input.closest(".filter-options");
    var $options = $optionsContainer.find(".filter-option[data-facet-item]");
    var $showMoreButton = $optionsContainer.find(".show-more-filters");
    var isSearching = filterValue.length > 0;

    if (!$optionsContainer.data("original-hidden-stored") && isSearching) {
      $options.each(function () {
        var $option = $(this);
        $option.data(
          "original-hidden",
          $option.hasClass("filter-option-hidden"),
        );
      });
      $optionsContainer.data("original-hidden-stored", true);
    }

    $options.each(function () {
      var $option = $(this);
      var text = $option.text().toLowerCase();
      var matches = text.indexOf(filterValue) > -1;

      if (isSearching) {
        if (matches) {
          $option.removeClass("filter-option-hidden");
        } else {
          $option.addClass("filter-option-hidden");
        }
      } else {
        var wasHidden = $option.data("original-hidden");
        if (wasHidden === true) {
          $option.addClass("filter-option-hidden");
        } else if (wasHidden === false) {
          $option.removeClass("filter-option-hidden");
        }
        $option.removeAttr("style");
      }
    });

    if (isSearching) {
      $showMoreButton.hide();
    } else {
      $optionsContainer.removeData("original-hidden-stored");
      updateHiddenItems($optionsContainer.closest(".filter-section"));
    }
  });

  // Collapse filter sections by default
  $(".filter-section").each(function () {
    var $section = $(this);
    var hasActive = $section.find(".filter-option.active").length > 0;
    var $toggle = $section.find(".filter-toggle");
    var $options = $section.find(".filter-options");
    var $icon = $toggle.find(".filter-icon");

    if (hasActive) {
      $options.show();
      $toggle.attr("aria-expanded", "true");
      $icon.css("transform", "rotate(180deg)");
    } else {
      $options.hide();
      $toggle.attr("aria-expanded", "false");
      $icon.css("transform", "rotate(0deg)");
    }

    updateHiddenItems($section);
  });

  // Handle "Show more" filters toggle
  $(document).on("click", ".show-more-filters", function () {
    var $button = $(this);
    var $section = $button.closest(".filter-section");
    var isExpanded = $button.hasClass("show-less");

    if (isExpanded) {
      $button.removeClass("show-less");
      $button.find("svg").css("transform", "rotate(0deg)");
      var count = $button.data("count");
      var textNode = $button.contents().filter(function () {
        return this.nodeType === 3;
      })[0];
      if (textNode) {
        textNode.textContent = getTranslation("show_more", count);
      }
    } else {
      $button.addClass("show-less");
      $button.find("svg").css("transform", "rotate(180deg)");
      var textNode = $button.contents().filter(function () {
        return this.nodeType === 3;
      })[0];
      if (textNode) {
        textNode.textContent = getTranslation("show_less");
      }
    }

    updateHiddenItems($section);
  });
});
