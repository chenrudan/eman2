/**
 * $Id$
 */
#include "lstio.h"
#include "log.h"
#include "emutil.h"
#include "util.h"

#include <string.h>

#ifndef WIN32
#include <sys/param.h>
#include <unistd.h>
#else
#include <direct.h>
#define M_PI 3.14159265358979323846
#define MAXPATHLEN 1024
#define getcwd _getcwd 
#endif

#include <assert.h>

using namespace EMAN;

const char *LstIO::MAGIC = "#LST";

LstIO::LstIO(string file, IOMode rw)
    :  filename(file), rw_mode(rw), lst_file(0)
{
    is_big_endian = ByteOrder::is_machine_big_endian();
    initialized = false;
    nimg = 0;
    imageio = 0;
    ref_filename = "";
    last_lst_index = -1;
    last_ref_index = -1;
}

LstIO::~LstIO()
{
    if (lst_file) {
	fclose(lst_file);
	lst_file = 0;
    }
    ref_filename = "";
}

int LstIO::init()
{
    static int err = 0;
    if (initialized) {
	return err;
    }
    Log::logger()->log("LstIO::init()");
    initialized = true;

    bool is_new_file = false;
    lst_file = sfopen(filename, rw_mode, &is_new_file);

    if (!lst_file) {
	err = 1;
	return err;
    }

    if (!is_new_file) {

	char buf[MAXPATHLEN];

	if (!fgets(buf, MAXPATHLEN, lst_file)) {
	    Log::logger()->error("cannot open LST file '%s'", filename.c_str());
	    err = 1;
	    return err;
	}

	if (!is_valid(&buf)) {
	    Log::logger()->error("%s is not a valid LST file", filename.c_str());
	    err = 1;
	    return err;
	}

	for (nimg = 0; fgets(buf, MAXPATHLEN, lst_file) != 0; nimg++) {
	    if (buf[0] == '#') {
		nimg--;
	    }
	}
	rewind(lst_file);
    }

    return 0;
}

bool LstIO::is_valid(const void *first_block)
{
    Log::logger()->log("LstIO::is_valid()");
    if (!first_block) {
	return false;
    }

    return Util::check_file_by_magic(first_block, MAGIC);
}

int LstIO::calc_ref_image_index(int image_index)
{
    if (image_index == last_lst_index) {
	return last_ref_index;
    }
    else {
	char buf[MAXPATHLEN];
	int step = image_index - last_lst_index;

	if (step < 0) {
	    rewind(lst_file);
	    step = image_index + 1;
	}

	for (int i = 0; i < step; i++) {
	    if (!fgets(buf, MAXPATHLEN, lst_file)) {
		Log::logger()->error("reach EOF in file '%s' before reading %dth image",
				     filename.c_str(), image_index);
		return 1;
	    }
	    if (buf[0] == '#') {
		i--;
	    }
	}
	int ref_image_index = 0;
	char ref_image_path[MAXPATHLEN];
	char unused[256];
	sscanf(buf, " %d %s %[ .,0-9-]", &ref_image_index, ref_image_path, unused);

	char fullpath[MAXPATHLEN];

	if (ref_image_path[0] == '/') {
	    strcpy(fullpath, ref_image_path);
	}
	else {
	    if (strrchr(filename.c_str(), '/')) {
		strcpy(fullpath, filename.c_str());
	    }
	    else {
		getcwd(fullpath, MAXPATHLEN);
	    }

	    char *p_basename = strrchr(fullpath, '/');
	    if (p_basename) {
		p_basename++;
		*p_basename = '\0';
		strcat(fullpath, ref_image_path);
	    }
	}

	ref_filename = string(fullpath);
	imageio = EMUtil::get_imageio(ref_filename, rw_mode);

	last_ref_index = ref_image_index;
    }

    last_lst_index = image_index;

    return last_ref_index;
}


int LstIO::read_header(Dict & dict, int image_index, const Region * area, bool is_3d)
{
    Log::logger()->log("LstIO::read_header() from file '%s'", filename.c_str());

    if (check_read_access(image_index) != 0) {
	return 1;
    }

    int ref_image_index = calc_ref_image_index(image_index);
    assert(imageio != 0);
    int err = imageio->read_header(dict, ref_image_index, area, is_3d);

    return err;
}

int LstIO::write_header(const Dict & , int )
{
    Log::logger()->log("LstIO::write_header() to file '%s'", filename.c_str());
    Log::logger()->warn("LST write header is not supported.");
    return 1;
}

int LstIO::read_data(float *data, int image_index, const Region * area, bool is_3d)
{
    Log::logger()->log("LstIO::read_data() from file '%s'", filename.c_str());

    if (check_read_access(image_index, true, data) != 0) {
	return 1;
    }

    int ref_image_index = calc_ref_image_index(image_index);
    assert(imageio != 0);
    int err = imageio->read_data(data, ref_image_index, area, is_3d);
    return err;
}

int LstIO::write_data(float *, int )
{
    Log::logger()->log("LstIO::write_data() to file '%s'", filename.c_str());
    Log::logger()->warn("LST write data is not supported.");
    return 1;

}



bool LstIO::is_complex_mode()
{
    return false;
}

bool LstIO::is_image_big_endian()
{
    return is_big_endian;
}

int LstIO::get_nimg()
{
    if (init() != 0) {
	return 0;
    }
    assert(nimg > 0);
    return nimg;
}
