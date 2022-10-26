/********************************************************************************
	RCP_HmsItemStar [ New New Version ]
														[ Nob 19, 1995 ]
 ********************************************************************************/
#include "convert_hms_to_geo_layouts.h"
#include "hms.h"
extern Gfx  RCP_star1[];
extern Gfx  RCP_star2[];
extern Gfx  RCP_star3[];
extern Gfx  RCP_star4[];
extern Gfx  RCP_star5[];
extern Gfx  RCP_star6[];
extern Gfx  RCP_star7[];
extern Gfx  RCP_star8[];

extern Gfx  RCP_star_dust1[];
extern Gfx  RCP_star_dust2[];
extern Gfx  RCP_star_dust3[];
extern Gfx  RCP_star_dust4[];
extern Gfx  RCP_star_dust5[];
extern Gfx  RCP_star_dust6[];
extern Gfx  RCP_star_dust7[];
extern Gfx  RCP_star_dust8[];


/********************************************************************************/
/*	Hierarchy data of star coin.												*/
/********************************************************************************/
Hierarchy RCP_HmsItemStar[] = {
	hmsShadow(100, 155, 1)
	hmsBegin()
		hmsSelect(8, ControlShapeAnime)
		hmsBegin()
			hmsGfx(RM_SPRITE, RCP_star1)
			hmsGfx(RM_SPRITE, RCP_star2)
			hmsGfx(RM_SPRITE, RCP_star3)
			hmsGfx(RM_SPRITE, RCP_star4)
			hmsGfx(RM_SPRITE, RCP_star5)
			hmsGfx(RM_SPRITE, RCP_star6)
			hmsGfx(RM_SPRITE, RCP_star7)
			hmsGfx(RM_SPRITE, RCP_star8)
		hmsEnd()
	hmsEnd()
	hmsExit()
};

/********************************************************************************/
/*	Hierarchy data of star dust.												*/
/********************************************************************************/
Hierarchy RCP_HmsItemStarDust[] = {
	hmsGroup()
	hmsBegin()
		hmsSelect(8, ControlShapeAnime)
		hmsBegin()
			hmsGfx(RM_SPRITE, RCP_star_dust1)
			hmsGfx(RM_SPRITE, RCP_star_dust2)
			hmsGfx(RM_SPRITE, RCP_star_dust3)
			hmsGfx(RM_SPRITE, RCP_star_dust4)
			hmsGfx(RM_SPRITE, RCP_star_dust5)
			hmsGfx(RM_SPRITE, RCP_star_dust6)
			hmsGfx(RM_SPRITE, RCP_star_dust7)
			hmsGfx(RM_SPRITE, RCP_star_dust8)
		hmsEnd()
	hmsEnd()
	hmsExit()
};
