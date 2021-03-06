#(set-default-paper-size "11x17" 'landscape)
#(set-global-staff-size 14)

\paper {
    bottom-margin = 10\mm
    right-margin = 10\mm
    top-margin = 10\mm
    left-margin = 30\mm

    evenFooterMarkup = \markup \fill-line {
        " "
        \concat {
            \bold \fontsize #3
            \on-the-fly #print-page-number-check-first
            \fromproperty #'page:page-number-string
            %\hspace #18
        }
    }
    oddFooterMarkup = \markup \fill-line {
        " "
        \concat {
            \bold \fontsize #3
            \on-the-fly #print-page-number-check-first
            \fromproperty #'page:page-number-string
            %\hspace #18
        }
    }

    oddHeaderMarkup = \markup \fill-line { " " }
    evenHeaderMarkup = \markup \fill-line { " " }

    page-breaking = #ly:optimal-breaking
    print-first-page-number = ##f
    print-page-number = ##t
    ragged-bottom = ##f
    ragged-last-bottom = ##t

    markup-system-spacing = #'(
        (basic-distance . 0)
        (minimum-distance . 12)
        (padding . 0)
        (stretchability . 100)
        )

    system-system-spacing = #'(
        (basic-distance . 0)
        (padding . 12)
        (stretchability . 100)
        )

    top-markup-spacing = #'(
        (basic-distance . 0)
        (minimum-distance . 0)
        (padding . 12)
        (stretchability . 100)
        )
}